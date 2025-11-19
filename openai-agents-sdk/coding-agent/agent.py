import asyncio
from tools.apply_patch import (
    apply_patch_tool,
    context7_tool,
)
from tools.shell_tool import shell_tool
from Instructions import CODING_AGENT_INSTRUCTIONS, UPDATED_INSTRUCTIONS
from agents import (
    Agent,
    Runner,
    WebSearchTool,
    ItemHelpers,
)


coding_agent = Agent(
    name="Coding Agent",
    model="gpt-5.1",
    instructions=UPDATED_INSTRUCTIONS,
    tools=[
        WebSearchTool(),
        shell_tool,
        apply_patch_tool,
        context7_tool,
    ],
)


async def run_updated_coding_agent_with_logs(prompt: str):
    """
    Run the updated coding agent (shell + web + apply_patch + Context7 MCP)
    and stream logs about what's happening.

    - Logs web_search, shell, apply_patch, and MCP (Context7) calls.
    - For apply_patch, logs the outputs returned by the editor.
    - At the end, shows a single "Apply all changes?" prompt for the tutorial.
    """
    print("=== Run starting ===")
    print(f"[user] {prompt}\n")

    apply_patch_seen = False

    result = Runner.run_streamed(
        coding_agent,
        input=prompt,
    )

    async for event in result.stream_events():
        if event.type != "run_item_stream_event":
            continue

        item = event.item

        # 1) Tool calls (function tools, web_search, shell, MCP, etc.)
        if item.type == "tool_call_item":
            raw = item.raw_item
            raw_type_name = type(raw).__name__

            # web_search (hosted Responses tool)
            if raw_type_name == "ResponseFunctionWebSearch":
                print("[tool] web_search – agent is calling web search")

            # shell (new ShellTool executor)
            elif raw_type_name == "LocalShellCall":
                action = getattr(raw, "action", None)
                commands = getattr(action, "commands", None) if action else None
                if commands:
                    print(f"[tool] shell – running commands: {commands}")
                else:
                    print("[tool] shell – running command")

            # MCP (e.g. Context7)
            elif "MCP" in raw_type_name or "Mcp" in raw_type_name:
                tool_name = getattr(raw, "tool_name", None)
                if tool_name is None:
                    action = getattr(raw, "action", None)
                    tool_name = getattr(action, "tool", None) if action else None
                server_label = getattr(raw, "server_label", None)
                label_str = f" (server={server_label})" if server_label else ""
                if tool_name:
                    print(f"[tool] mcp{label_str} – calling tool {tool_name!r}")
                else:
                    print(f"[tool] mcp{label_str} – MCP tool call")

            # Generic fallback for other tools (including hosted ones)
            else:
                print(f"[tool] {raw_type_name} called")

        # 2) Tool call outputs (where apply_patch shows up)
        elif item.type == "tool_call_output_item":
            raw = item.raw_item
            output_preview = str(item.output)

            # Detect apply_patch via raw_item type or output format
            is_apply_patch = False
            if isinstance(raw, dict) and raw.get("type") == "apply_patch_call_output":
                is_apply_patch = True
            elif any(
                output_preview.startswith(prefix)
                for prefix in ("Created ", "Updated ", "Deleted ")
            ):
                is_apply_patch = True

            if is_apply_patch:
                apply_patch_seen = True
                if len(output_preview) > 400:
                    output_preview = output_preview[:400] + "…"
                print(f"[apply_patch] {output_preview}\n")
            else:
                if len(output_preview) > 400:
                    output_preview = output_preview[:400] + "…"
                print(f"[tool output]\n{output_preview}\n")

        # 3) Normal assistant messages
        elif item.type == "message_output_item":
            text = ItemHelpers.text_message_output(item)
            print(f"[assistant]\n{text}\n")

        # 4) Other event types – ignore for now
        else:
            pass

    print("=== Run complete ===\n")

    # Final answer
    print("Final answer:\n")
    print(result.final_output)

    # Single end-of-run confirmation about edits
    if apply_patch_seen:
        _ = print("\n[apply_patch] One or more apply_patch calls were executed.")
    else:
        print("\n[apply_patch] No apply_patch calls detected in this run.")


edit_prompt = """Update the dashboard to add a 'summarize' button in the top right corner.
When clicked, use the OpenAI Responses API with the gpt-5.1 model to generate a summary of the metrics on the dashboard, and display it in a modal."""

if __name__ == "__main__":
    asyncio.run(run_updated_coding_agent_with_logs(edit_prompt))
