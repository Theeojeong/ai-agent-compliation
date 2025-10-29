from dotenv import load_dotenv

load_dotenv()

from google.adk.models.lite_llm import LiteLlm
from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH

history_agent = RemoteA2aAgent(
    name="HistoryHelperAgent",
    description="An agent that can help students with their history homework.",
    agent_card=f"http://127.0.0.1:8001{AGENT_CARD_WELL_KNOWN_PATH}",
)

root_agent = LlmAgent(
    name="StudentHelperAgent",
    description="An agent that can be helps students with their homework.",
    model=LiteLlm(model="openai/gpt-5-mini"),
    sub_agents=[history_agent],
)
