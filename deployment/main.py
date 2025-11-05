from agents import Agent, Runner
from dotenv import load_dotenv
from fastapi import FastAPI
from openai import AsyncOpenAI
from pydantic import BaseModel


load_dotenv()

agent = Agent(name="Assistant", instructions="You help users with their questions.")

class CreateConversationResponse(BaseModel):
    conversation_id: str

app = FastAPI()

client = AsyncOpenAI()


@app.post("/conversation")
async def create_conversation_id() -> CreateConversationResponse:

    conversation = await client.conversations.create()

    return {
        "conversation_id": conversation.id
    }
