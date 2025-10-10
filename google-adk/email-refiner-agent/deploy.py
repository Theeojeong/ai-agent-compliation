import vertexai
from travel_advisor_agent.agent import travel_advisor_agent
from vertexai.preview import reasoning_engines
from dotenv import load_dotenv
import os

load_dotenv()

PROJECT_ID = "theo-project-441505"
LOCATION = "asia-northeast1"
BUCKET = "gs://theo-agent"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=BUCKET,
)

app = reasoning_engines.AdkApp(
    agent=travel_advisor_agent,
    enable_tracing=True,
)

remote_app = vertexai.agent_engines.create(
    display_name="Travel Advisor Agent",
    agent_engine=app,
    requirements=[
        "litellm",
        "google-cloud-aiplatform[adk,agent_engines]",
    ],
    extra_packages=[
        "travel_advisor_agent",
    ],
    env_vars={
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
    },
)
