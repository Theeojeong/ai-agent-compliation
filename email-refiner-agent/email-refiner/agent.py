from google.adk.agents import Agent, LoopAgent
from google.adk.tools.tool_context import ToolContext
from google.adk.models.lite_llm import LiteLlm
from .prompt import (
    CLARITY_EDITOR_DESCRIPTION,
    TONE_STYLIST_DESCRIPTION,
    PERSUASION_STRATEGIST_DESCRIPTION,
    EMAIL_SYNTHESIZER_DESCRIPTION,
    LITERARY_CRITIC_DESCRIPTION,
    EMAIL_OPTIMIZER_DESCRIPTION,
    CLARITY_EDITOR_INSTRUCTION,
    TONE_STYLIST_INSTRUCTION,
    PERSUASION_STRATEGIST_INSTRUCTION,
    EMAIL_SYNTHESIZER_INSTRUCTION,
    LITERARY_CRITIC_INSTRUCTION,
)

MODEL = LiteLlm("openai/gpt-4o")


def escalate_email_complete(tool_context: ToolContext):
    """Use this tool only when the email is good to go."""
    tool_context.actions.escalate = True
    return "Email optimization complete."


clarity_agent = Agent(
    name="ClarityAgent",
    instruction=CLARITY_EDITOR_INSTRUCTION,
    description=CLARITY_EDITOR_DESCRIPTION,
    model=MODEL,
    output_key="clarity_output",
)

tone_stylist_agent = Agent(
    name="ToneStylistAgent",
    description=TONE_STYLIST_DESCRIPTION,
    instruction=TONE_STYLIST_INSTRUCTION,
    model=MODEL,
    output_key="tone_output",
)

persuation_strategist_agent = Agent(
    name="PersuationStrategistAgent",
    instruction=PERSUASION_STRATEGIST_INSTRUCTION,
    description=PERSUASION_STRATEGIST_DESCRIPTION,
    model=MODEL,
    output_key="persuasion_output",
)

email_synthesizer_agent = Agent(
    name="EmailSynthesizerAgent",
    instruction=EMAIL_SYNTHESIZER_INSTRUCTION,
    description=EMAIL_SYNTHESIZER_DESCRIPTION,
    model=MODEL,
    output_key="synthesized_output",
)

literary_critic_agent = Agent(
    name="LiteraryCriticAgent",
    description=LITERARY_CRITIC_DESCRIPTION,
    instruction=LITERARY_CRITIC_INSTRUCTION,
    model=MODEL,
    tools=[escalate_email_complete,],
)


email_refiner_agent = LoopAgent(
    name="EmailRefinerAgent",
    description=EMAIL_OPTIMIZER_DESCRIPTION,
    sub_agents=[
        clarity_agent,
        tone_stylist_agent,
        persuation_strategist_agent,
        email_synthesizer_agent,
        literary_critic_agent,
    ],
    max_iterations=50,
)

# root_agent = email_refiner_agent
