from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .prompt import IMAGE_BUILDER_DESCRIPTION, IMAGE_BUILDER_PROMPT
from .tools import generate_images

MODEL = LiteLlm("openai/gpt-4o")

image_builder_agent = Agent(
    name="ImageBuilderAgent",
    description=IMAGE_BUILDER_DESCRIPTION,
    instruction=IMAGE_BUILDER_PROMPT,
    tools=[
        generate_images,
    ],
    model=MODEL,
    output_key="image_builder_output",
)
