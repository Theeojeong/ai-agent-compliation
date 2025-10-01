from dotenv import load_dotenv

load_dotenv()

import streamlit as st
import asyncio
import openai
from agents import Agent, Runner, SQLiteSession, function_tool, RunContextWrapper
from models import UserAccountContext
from my_agents.triage_agent import triage_agent


@function_tool
def get_user_tier(wrapper: RunContextWrapper[UserAccountContext]):
    return (
        f"The user {wrapper.context.customer_id} has a {wrapper.context.tier} account."
    )


client = openai.OpenAI()

user_account_context = UserAccountContext(name="theo", customer_id=1, tier="basic")

if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        session_id="user_1", db_path="customer-support-agent.db"
    )

session = st.session_state["session"]


async def paint_history():
    messages = await session.get_items()
    for message in messages:
        if "role" in message:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.write(message["content"])
                else:
                    if message["type"] == "message":
                        st.write(message["content"][0]["text"])


asyncio.run(paint_history())


async def run_agent(prompt):
    with st.chat_message("ai"):
        text_placeholder = st.empty()
        response = ""
        stream = Runner.run_streamed(
            triage_agent, prompt, session=session, context=user_account_context
        )

        async for event in stream.stream_events():
            if event.type == "raw_response_event":

                if event.data.type == "response.output_text.delta":
                    response += event.data.delta
                    text_placeholder.write(response)


prompt = st.chat_input("Agent에게 질문해 주세요.")

if prompt:

    with st.chat_message("human"):
        st.write(prompt)
    asyncio.run(run_agent(prompt))

with st.sidebar:
    reset = st.button("Reset memory")
    if reset:
        asyncio.run(session.clear_session())
    st.write(asyncio.run(session.get_items()))
