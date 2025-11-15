import sys
import asyncio

import os
import re
from dotenv import load_dotenv
from collections.abc import Sequence
from pathlib import Path
from typing import Literal

from agents import (
    ShellTool,
    ShellCommandRequest,
    ShellCommandOutput,
    ShellCallOutcome,
    ShellResult,
    Agent,
    Runner,
    WebSearchTool,
    ItemHelpers,
    RunConfig,
)

load_dotenv()

workspace_dir = Path("workspace_dir").resolve()
workspace_dir.mkdir(exist_ok=True)

print(f"Workspace directory: {workspace_dir}")

async def require_approval(commands: Sequence[str]) -> None:  # approval: 승인
    """
    셸 명령을 실행하기 전에 확인을 요청합니다.

    환경 변수에 SHELL_AUTO_APPROVE=1을 설정하면 이 프롬프트를 건너뜁니다
    (반복 작업이 많거나 CI에서 실행할 때 유용합니다).
    """
    if os.environ.get("SHELL_AUTO_APPROVE") == "1":
        return

    print("Shell command approval required:")
    for entry in commands:
        print(" ", entry)
    response = input("Proceed? [y/N]").strip().lower()
    if response not in {"y", "yes"}:
        raise RuntimeError("Shell command execution rejected by user.")


class ShellExecutor:  # Excutor: 집행자
    """
    노트북 쿡북을 위한 셸 실행자입니다.

    - 모든 명령을 `workspace_dir` 내에서 실행합니다
    - stdout/stderr를 캡처합니다
    - `action.timeout_ms`로부터 선택적 타임아웃을 적용합니다
    - ShellCallOutcome을 사용하여 ShellCommandOutput 항목이 포함된 ShellResult를 반환합니다
    """

    def __init__(self, cwd: Path):
        self.cwd = cwd

    async def __call__(self, request: ShellCommandRequest) -> ShellResult:
        action = request.data.action
        await require_approval(action.commands)

        outputs: list[ShellCommandOutput] = []

        for command in action.commands:
            prepared_command = self._prepare_command(command)

            proc = await asyncio.create_subprocess_shell(
                prepared_command,
                cwd=self.cwd,
                env=self._build_env(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            timed_out = False
            try:
                timeout = (action.timeout_ms or 0) / 1000 or None
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                proc.kill()
                stdout_bytes, stderr_bytes = await proc.communicate()
                timed_out = True

            stdout = stdout_bytes.decode("utf-8", errors="ignore")
            stderr = stderr_bytes.decode("utf-8", errors="ignore")

            # Use ShellCallOutcome instead of exit_code/status fields directly
            outcome = ShellCallOutcome(
                type="timeout" if timed_out else "exit",
                exit_code=getattr(proc, "returncode", None),
            )

            outputs.append(
                ShellCommandOutput(
                    command=command,
                    stdout=stdout,
                    stderr=stderr,
                    outcome=outcome,
                )
            )

            if timed_out:
                # Stop running further commands if this one timed out
                break

        return ShellResult(
            output=outputs,
            provider_data={"working_directory": str(self.cwd)},
        )

    def _build_env(self) -> dict[str, str]:
        env = os.environ.copy()
        env.setdefault("npm_config_yes", "true")
        return env

    def _prepare_command(self, command: str) -> str:
        if os.name != "nt":
            return command

        updated = command

        updated = updated.replace("|| true", "")
        updated = self._replace_token(updated, "pwd", "cd")
        updated = self._replace_token(updated, "ls", "dir")

        updated = self._ensure_npx_yes(updated)

        return updated

    @staticmethod
    def _replace_token(command: str, token: str, replacement: str) -> str:
        pattern = rf"(?<![\\w./-]){re.escape(token)}(?![\\w./-])"
        return re.sub(pattern, replacement, command)

    @staticmethod
    def _ensure_npx_yes(command: str) -> str:
        stripped = command.lstrip()
        if not stripped.startswith("npx "):
            return command
        if "--yes" in stripped:
            return command
        prefix_length = len(command) - len(stripped)
        return command[:prefix_length] + stripped.replace("npx ", "npx --yes ", 1)


shell_tool = ShellTool(executor=ShellExecutor(cwd=workspace_dir))


# Define the agent's instructions
INSTRUCTIONS = """
You are a coding assistant. The user will explain what they want to build, and your goal is to run commands to generate a new app.
You can search the web to find which command you should use based on the technical stack, and use commands to create code files. 
You should also install necessary dependencies for the project to work. 
"""


coding_agent = Agent(
    name="Coding Agent",
    model="gpt-5.1",
    instructions=INSTRUCTIONS,
    tools=[WebSearchTool(), shell_tool],
)


async def run_coding_agent_with_logs(prompt: str):
    """
    Run the coding agent and stream logs about what's happening
    """
    print("=== Run starting ===")
    print(f"[user] {prompt}\n")

    result = Runner.run_streamed(coding_agent, input=prompt)

    async for event in result.stream_events():

        # High-level items: messages, tool calls, tool outputs, MCP, etc.
        if event.type == "run_item_stream_event":
            item = event.item

            # 1) Tool calls (function tools, web_search, shell, MCP, etc.)
            if item.type == "tool_call_item":
                raw = item.raw_item
                raw_type_name = type(raw).__name__

                # Special-case the ones we care most about in this cookbook
                if raw_type_name == "ResponseFunctionWebSearch":
                    print("[tool] web_search_call – agent is calling web search")
                elif raw_type_name == "LocalShellCall":
                    # LocalShellCall.action.commands is where the commands live
                    commands = getattr(getattr(raw, "action", None), "commands", None)
                    if commands:
                        print(f"[tool] shell – running commands: {commands}")
                    else:
                        print("[tool] shell – running command")
                else:
                    # Generic fallback for other tools (MCP, function tools, etc.)
                    print(f"[tool] {raw_type_name} called")

            # 2) Tool call outputs
            elif item.type == "tool_call_output_item":
                # item.output is whatever your tool returned (could be structured)
                output_preview = str(item.output)
                if len(output_preview) > 400:
                    output_preview = output_preview[:400] + "…"
                print(f"[tool output] {output_preview}")

            # 3) Normal assistant messages
            elif item.type == "message_output_item":
                text = ItemHelpers.text_message_output(item)
                print(f"[assistant]\n{text}\n")

            # 4) Other event types (reasoning, MCP list tools, etc.) – ignore
            else:
                pass

    print("=== Run complete ===\n")

    # Once streaming is done, result.final_output contains the final answer
    print("Final answer:\n")
    print(result.final_output)

prompt = "Create a new NextJS app that shows dashboard-01 from https://ui.shadcn.com/blocks on the home page"

if __name__ == "__main__":
    asyncio.run(run_coding_agent_with_logs(prompt))
