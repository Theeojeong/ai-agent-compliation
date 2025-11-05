from fastapi import FastAPI, Request
from dotenv import load_dotenv
import logging
from graph import graph

load_dotenv()

logger = logging.getLogger(__name__)

app = FastAPI()


def hadle_message(message: str):

    response = graph.invoke({"messages": [{"role": "user", "content": message}]})

    return response['messages'][-1].content


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
    body2.reverse()

    message_texts = ""

    for message in body2:
        text = message.get('text')
        message_texts += f"{text}\n"

    result = hadle_message(message_texts)

    return {
        "id": "message_1",
        "jsonrpc": "2.0",
        "result": {
            "kind": "message",
            "message_id": "239827493847289374",
            "role": "agent",
            "parts": [
                {"kind": "text", "text": result},
            ],
        },
    }
