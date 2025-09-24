from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from agents import Agent, SQLiteSession, Runner
import asyncio


if "agent" not in st.session_state:
    st.session_state["agent"] = Agent(
        name="ChatGPT Clone",
        instructions="You are a helpful assistant."
    )

agent = st.session_state["agent"]

if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        "user1",
        "user-memory.db"
    )

session = st.session_state["session"]

#=================================== UI ==========================================

async def run_agent(message):
    stream = Runner.run_streamed(
        agent,
        message,
        session=session
    )
    async for event in stream.stream_events():
        if event.type == "raw_response_event":
            if event.data.type == "response.output_text.delta":
                with st.chat_message('ai'):
                    st.write_stream(event.data.delta)

prompt = st.chat_input("agent에게 질문해주세요.")

if prompt:
    with st.chat_message('user'):
        st.write(prompt)
    asyncio.run(run_agent(prompt))

with st.sidebar:
    push = st.button("db 초기화 버튼")
    if push:
        asyncio.run(session.clear_session())
    st.write(asyncio.run(session.get_items()))