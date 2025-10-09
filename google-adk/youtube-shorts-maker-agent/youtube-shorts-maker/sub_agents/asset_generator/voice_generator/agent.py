from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .tools import generate_narrations
from .prompt import VOICE_GENERATOR_DESCRIPTION, VOICE_GENERATOR_PROMPT

MODEL = LiteLlm("openai/gpt-4o")

voice_generator_agent = Agent(
    name="VoiceGeneratorAgent",
    instruction=VOICE_GENERATOR_PROMPT,
    description=VOICE_GENERATOR_DESCRIPTION,
    model=MODEL,
    tools=[
        generate_narrations,
    ],
)
