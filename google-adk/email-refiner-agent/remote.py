from google.cloud.aiplatform_v1 import DeploymentStage
import vertexai
from vertexai import agent_engines

PROJECT_ID = "theo-project-441505"
LOCATION = "asia-northeast1"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
)

# deployments = agent_engines.list()

# for deployment in deployments:
#     print(deployment)
#     print("="*50)

DEPLOYMENT_ID = "projects/960578659657/locations/asia-northeast1/reasoningEngines/7892048173571506176"

remote_app = agent_engines.get(DEPLOYMENT_ID)

# print(remote_app.display_name)

# remote_session = remote_app.create_session(user_id="theo")

# print(remote_session['id'])

SESSION_ID = "8739882139505393664"

for event in remote_app.stream_query(
    user_id="theo",
    session_id=SESSION_ID,
    message="베이징 여행을 계획하려해"
):
    print(event)

remote_app.delete(force=True)