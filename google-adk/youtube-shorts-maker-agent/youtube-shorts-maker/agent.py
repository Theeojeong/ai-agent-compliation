from google.adk.agents import Agent
from google.genai import types
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.agent_tool import AgentTool
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.agents.callback_context import CallbackContext
from .sub_agents.content_planner.agent import content_planner_agent
from .sub_agents.asset_generator.agent import asset_generator_agent
from .sub_agents.video_assembler.agent import video_assembler_agent
from .prompt import SHORTS_PRODUCER_DESCRIPTION, SHORTS_PRODUCER_PROMPT

MODEL = LiteLlm("openai/gpt-4o")


def before_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
):

    history = llm_request.contents
    last_message = history[-1]
    if last_message.role == "user":
        text = last_message.parts[0].text
        if "국뽕" in text:
            return LlmResponse(
                content=types.Content(
                    parts=[
                        types.Part(
                            text="죄송합니다, 고객님의 요청을 도와드릴 수 없습니다."
                        )
                    ],
                    role="model",
                )
            )

    return None


shorts_producer_agent = Agent(
    name="ShortsProducerAgent",
    description=SHORTS_PRODUCER_DESCRIPTION,
    instruction=SHORTS_PRODUCER_PROMPT,
    model=MODEL,
    tools=[
        AgentTool(agent=content_planner_agent),
        AgentTool(agent=asset_generator_agent),
        AgentTool(agent=video_assembler_agent),
    ],
    before_model_callback=before_model_callback,
)

root_agent = shorts_producer_agent
