from dotenv import load_dotenv
load_dotenv()
import os
from openai import OpenAI
import streamlit as st
import base64
from agents import Agent, SQLiteSession, Runner, WebSearchTool, FileSearchTool
import asyncio

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

VECTOR_STORE_ID = "vs_68d54976ba1081918d88a11c80b1e5e8"

if "agent" not in st.session_state:
    st.session_state["agent"] = Agent(
        name="ChatGPT Clone",
        instructions="""
        You are a helpful assistant.

        You have access to the followign tools:
            - Web Search Tool: Use this when the user asks a questions that isn't in your training data. Use this tool when the users asks about current or future events, when you think you don't know the answer, try searching for it in the web first.
            - File Search Tool: Use this tool when the user asks a question about facts related to themselves. Or when they ask questions about specific files. 파일에 명시되어 있지 않은 정보는 웹서치 도구를 활용하세요.
        """,
        tools=[
            WebSearchTool(), 
            FileSearchTool(
            vector_store_ids=[VECTOR_STORE_ID],
            max_num_results=3
        )]
    )
agent = st.session_state["agent"]

if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        "user1",
        "user-memory.db"
    )

session = st.session_state["session"]

#=================================== UI ==========================================

st.header("Chat GPT Clone!")

async def paint_history():
    messages = await session.get_items()

    for message in messages:
        if "role" in message:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    content = message["content"]
                    if isinstance(content, str):
                        st.write(content)
                    elif isinstance(content, list):
                        for part in content:
                            if "image_url" in part:
                                st.image(part["image_url"])
                else:
                    if message['type'] == "message": 
                        st.write(message['content'][0]['text'])

        if "type" in message:
            if message["type"] == "web_search_call":
                with st.chat_message('ai'):
                    st.write("🔍 Searched the web...")

            elif message["type"] == "file_search_call":
                with st.chat_message('ai'):
                    st.write("🔍 Searched the files...")

asyncio.run(paint_history())
#==================================== RUN =========================================

def update_status(status_container, event):
    status_message = {"response.web_search_call.completed": ("웹 서치 완료", "complete"),
        "response.web_search_call.in_progress": ("웹 서치 진행 중", "running"),
        "response.web_search_call.searching": ("웹 서치 진행 중", "running"),
        'response.file_search_call.completed': ("파일 탐색 완료", "complete"),
        'response.file_search_call.in_progress': ("파일 탐색 중", "running"),
        'response.file_search_call.searching': ("파일 탐색 중", "running"),
        "response.completed": (" ", "complete")
        }

    if event in status_message:
            label, state = status_message[event]
            status_container.update(label=label, state=state)
#==================================== RUN =========================================

async def run_agent(message):
    with st.chat_message('ai'):
        status_container = st.status("⏳", expanded=False)
        text_placeholder = st.empty()
        response = ""

        stream = Runner.run_streamed(
            agent,
            message,
            session=session
        )

        async for event in stream.stream_events():
            if event.type == "raw_response_event":

                update_status(status_container, event.data.type)

                if event.data.type == "response.output_text.delta":
                    response += event.data.delta
                    text_placeholder.write(response)

prompt = st.chat_input(
    "Agent에게 질문해주세요. 이미지 업로드 가능",
    accept_file=True,
    file_type=[
        "txt",
        "jpg",
        "jpeg",
        "png"
    ]
)

if prompt:
    for file in prompt.files:
        if file.type.startswith("text/"):
            with st.chat_message('ai'):
                with st.status("⏳ Uploading File...") as status:
                    uploaded_file = client.files.create(
                        file=(file.name, file.getvalue()),
                        purpose="user_data",
                    )
                    status.update(label="⏳ Attaching file..."),
                    client.vector_stores.files.create(
                        vector_store_id=VECTOR_STORE_ID,
                        file_id=uploaded_file.id
                    )
                    status.update(label="✅ File uploaded", state="complete")
        elif file.type.startswith("image/"):
            with st.chat_message('ai'):
                with st.status("⏳ Uploading Image...") as status:
                    file_byte = file.getvalue()
                    base64_data = base64.b64encode(file_byte).decode("utf-8")
                    data_url = f"data:{file.type};base64,{base64_data}"
                    asyncio.run(
                        session.add_items(
                            [
                                {
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "input_image",
                                            "detail": "auto",
                                            "image_url": data_url
                                        }
                                    ]
                                }
                            ]
                        )
                    )
                    status.update(label="✅ Image uploaded", state="complete")
                with st.chat_message("user"):
                    st.image(data_url)
    if prompt.text:
        with st.chat_message('user'):
            st.write(prompt.text)
        asyncio.run(run_agent(prompt.text))

with st.sidebar:
    push = st.button("db 초기화 버튼")
    if push:
        asyncio.run(session.clear_session())
    st.write(asyncio.run(session.get_items()))