from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .prompt import VIDEO_ASSEMBLER_DESCRIPTION, VIDEO_ASSEMBLER_PROMPT
from .tools import assemble_video

MODEL = LiteLlm("openai/gpt-4o")

video_assembler_agent = Agent(
    name="VideoAssemblerAgent",
    description=VIDEO_ASSEMBLER_DESCRIPTION,
    instruction=VIDEO_ASSEMBLER_PROMPT,
    tools=[assemble_video,],
    model=MODEL,
    output_key="video_assembler_output",
)
