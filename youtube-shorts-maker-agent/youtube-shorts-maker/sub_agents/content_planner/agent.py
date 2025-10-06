from ast import Pass
from google.adk.agents import Agent
from .prompt import CONTENT_PLANNER_DESCRIPTION, CONTENT_PLANNER_PROMPT
from google.adk.models.lite_llm import LiteLlm
from pydantic import BaseModel, Field
from typing import List

MODEL = LiteLlm("openai/gpt-4o")

class ScenesOutput(BaseModel):

    id: int = Field(description="Scene ID number")
    narration: str = Field(description="Narration text for the scene")
    visual_description: str = Field(
        description="Detailed description for image generation"
    )
    embedded_text: str = Field(
        description="Text overlay for the image (can be any case/style)"
    )
    embedded_text_location: str = Field(
        description="Where to position the text on the image (e.g., 'top center', 'bottom left', 'middle right', 'center')"
    )
    duration: str = Field(description="Duration in seconds for this scene")


class ContentPlannerOutput(BaseModel):

    topic: str = Field(description="The topic of the YouTube Short")
    total_duration: str = Field(description="Total video duration in seconds (max 20)")
    scenes: List[ScenesOutput] = Field(
        description="List of scenes (agent decides how many)"
    )


content_planner_agent = Agent(
    name="ContentPlannerAgent",
    description=CONTENT_PLANNER_DESCRIPTION,
    instruction=CONTENT_PLANNER_PROMPT,
    model=MODEL,
    output_schema=ContentPlannerOutput,
    output_key="content_planner_output"
)
