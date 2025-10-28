from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.a2a.utils.agent_to_a2a import to_a2a


agent = LlmAgent(
    name="HistoryHelperAgent",
    description="An agent that can help students with their history homework.",
    model=LiteLlm(model="openai/gpt-5-mini"),
    sub_agents=[]
)

app = to_a2a(agent=agent)
