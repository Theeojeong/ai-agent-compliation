from fastapi import FastAPI, Request
from dotenv import load_dotenv
from graph import graph

load_dotenv()

app = FastAPI()


def hadle_message():

    graph.invoke()


@app.get("/.well-known/agent-card.json")
def get_agent_card():
    return {
        "capabilities": {},
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain"],
        "description": "An agent that can help students with their philosophy homework.",
        "name": "PhilosophyHelperAgent",
        "preferredTransport": "JSONRPC",
        "protocolVersion": "0.3.0",
        "skills": [
            {
                "description": "An agent that can help students with their philosophy homework.",
                "id": "PhilosophyHelperAgent",
                "name": "model",
                "tags": ["llm"],
            }
        ],
        "supportsAuthenticatedExtendedCard": False,
        "url": "http://localhost:8002",
        "version": "0.0.1",
    }


@app.post("/")
async def handle_message(req: Request):
    body = await req.json()
    body2 = body.get("params").get("message").get("parts")
    print(body2)
    return {
        "return": body
    }
