import asyncio
import os
import re

from dotenv import load_dotenv
from collections.abc import Sequence
from pathlib import Path

from agents import (
    ShellTool,
    ShellCommandRequest,
    ShellCommandOutput,
    ShellCallOutcome,
    ShellResult,
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
