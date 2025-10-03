from unittest import TextTestResult
from dotenv import load_dotenv

load_dotenv()

import streamlit as st
import asyncio
import openai
from agents import (
    Runner,
    SQLiteSession,
    RunContextWrapper,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
)
from models import UserAccountContext
from my_agents.triage_agent import triage_agent

client = openai.OpenAI()

# ========================User Info=========================

user_account_context = UserAccountContext(
    name="JEONG JAEHYEON",
    customer_id=1,
    tier="Premium",
)

# ========================UI=========================

if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        session_id="user_1",
        db_path="customer-support-agent.db",
    )
session = st.session_state["session"]

if "agent" not in st.session_state:
    st.session_state["agent"] = triage_agent


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

# ========================Main=========================


async def run_agent(prompt):
    with st.chat_message("ai"):
        text_placeholder = st.empty()
        response = ""

        st.session_state['text_placeholder'] = text_placeholder

        try:
            stream = Runner.run_streamed(
                triage_agent,
                prompt,
                session=session,
                context=user_account_context,
            )

            async for event in stream.stream_events():
                if event.type == "raw_response_event":

                    if event.data.type == "response.output_text.delta":
                        response += event.data.delta
                        text_placeholder.write(response)

                elif event.type == "agent_updated_stream_event":
                    if st.session_state["agent"].name != event.new_agent.name:

                        st.write(
                            f"🤖 Transfered from @{st.session_state['agent'].name} to @{event.new_agent.name}",
                        )

                        st.session_state["agent"] == event.new_agent

                        text_placeholder = st.empty()

                        st.session_state['text_placeholder'] = text_placeholder
                        response = ""

        except InputGuardrailTripwireTriggered:
            st.write("질문에 답변할 수 없습니다")
        except OutputGuardrailTripwireTriggered:
            st.write("질문에 답변할 수 없습니다")
            st.session_state["text_placeholder"] = st.empty()


prompt = st.chat_input("Agent에게 질문해 주세요.")

if prompt:

    with st.chat_message("human"):
        st.write(prompt)
    asyncio.run(run_agent(prompt))


# ========================SideBar=========================

with st.sidebar:
    reset = st.button("Reset memory")
    if reset:
        asyncio.run(session.clear_session())
    st.write(asyncio.run(session.get_items()))
