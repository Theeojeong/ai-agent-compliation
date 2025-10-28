from google.adk.models.lite_llm import LiteLlm
from google.adk.agents import LlmAgent

agent = LlmAgent(
    name="StudentHelperAgent",
    description="An agent that can be helps students with their homework.",
    model=LiteLlm(model="openai/gpt-5-mini"),
    sub_agents=[]
)

root_agent = agent