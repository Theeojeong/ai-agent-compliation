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

async def paint_history():
    messages = await session.get_items()

    for message in messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.write(message['content'])
            else:
                if message['type'] == "message": 
                    st.write(message['content'][0]['text'])

asyncio.run(paint_history())

async def run_agent(message):
    with st.chat_message('ai'):
        text_placeholder = st.empty()
        response = ""
        stream = Runner.run_streamed(
            agent,
            message,
            session=session
        )
        async for event in stream.stream_events():
            if event.type == "raw_response_event":
                if event.data.type == "response.output_text.delta":
                    response += event.data.delta
                    text_placeholder.write(response)

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