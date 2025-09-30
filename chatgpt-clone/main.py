from dotenv import load_dotenv
load_dotenv()
import openai
from openai import OpenAI
import streamlit as st
import base64
from agents import (
    Agent, 
    SQLiteSession, 
    Runner, 
    WebSearchTool, 
    FileSearchTool,
    ImageGenerationTool,
    CodeInterpreterTool,
    HostedMCPTool
    )
import asyncio

from agents.mcp.server import MCPServerStdio

client = OpenAI()

VECTOR_STORE_ID = "vs_68d54976ba1081918d88a11c80b1e5e8"

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

            elif message["type"] == "image_generation_call":
                with st.chat_message('ai'):
                    image = base64.b64decode(message["result"])
                    st.image(image)
            elif message["type"] == "code_interpreter_call":
                with st.chat_message('ai'):
                    st.code(message['code'])
            elif message["type"] == "mcp_list_tools":
                with st.chat_message('ai'):
                    st.write(message['server_label'])

asyncio.run(paint_history())
#==================================== RUN =========================================

def update_status(status_container, event):
    status_message = {"response.web_search_call.completed": ("웹 서치 완료", "complete"),
        "response.web_search_call.in_progress": ("웹 서치 진행 중", "running"),
        "response.web_search_call.searching": ("웹 서치 진행 중", "running"),
        'response.file_search_call.completed': ("파일 탐색 완료", "complete"),
        'response.file_search_call.in_progress': ("파일 탐색 중", "running"),
        'response.file_search_call.searching': ("파일 탐색 중", "running"),
        'response.image_generation_call.completed': ("이미지 생성 완료", "complete"),
        'response.image_generation_call.generating': ("이미지 생성 중", "running"),
        'response.image_generation_call.in_progress': ("이미지 생성 중", "running"),
        'response.image_generation_call.partial_image':("이미지 생성 중", "running"),
        'response.code_interpreter_call_code.done': ("코드 작성 중", "running"),
        'response.code_interpreter_call.completed': ("코드 작성 완료", "complete"),
        'response.code_interpreter_call.in_progress': ("코드 작성 중", "running"),
        'response.code_interpreter_call.interpreting':("코드 작성 중", "running"),
        'response.mcp_call_arguments.delta': ("mcp 호출 중", "running") , 
        'response.mcp_call_arguments.done': ("mcp 호출 중", "complete"), 
        'response.mcp_call.completed': ("mcp 호출 완료", "running"), 
        'response.mcp_call.failed': ("mcp 호출 실패", "error"), 
        'response.mcp_call.in_progress': ("mcp 호출 중", "running"), 
        'response.mcp_list_tools.completed': ("MCP 도구 목록 가져오기 완료", "complete"), 
        'response.mcp_list_tools.failed': ("MCP 도구 목록 가져오기 실패", "error"), 
        'response.mcp_list_tools.in_progress': ("MCP 도구 목록을 가져오는 중", "running"),
        "response.completed": (" ", "complete")
        }

    if event in status_message:
            label, state = status_message[event]
            status_container.update(label=label, state=state)
#==================================== RUN =========================================

async def run_agent(message):
    yhfinance_mcp = MCPServerStdio(
        params={
            "command": "uvx",
            "args": ["mcp-yahoo-finance"]
        },
        cache_tools_list=True
    )
    timezone_server = MCPServerStdio(
        params={
            "command": "uvx",
            "args": ["mcp-server-time", "--local-timezone=Asia/Seoul"]
        }
    )

    async with yhfinance_mcp, timezone_server:
        agent = Agent(
            mcp_servers=[
                yhfinance_mcp,
                timezone_server,
            ],
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
            ),
                ImageGenerationTool(
                    tool_config={
                        "type": "image_generation",
                        "quality": "high",
                        "output_format": "jpeg",
                        "partial_images": 1,
                    }
                ),
                CodeInterpreterTool(
                    tool_config={
                        "type": "code_interpreter",
                        "container":{
                            "type": "auto",
                        }
                    }
                ),
                HostedMCPTool(
                    tool_config={
                        "type": "mcp",
                        "server_label": "context7",
                        "server_url": "https://mcp.context7.com/mcp",
                        "server_description": "Use this to get the docs from software projects.",
                        "require_approval": "never"
                    }
                )
        ]
    )
        with st.chat_message('ai'):
            status_container = st.status("⏳", expanded=False)
            code_placeholder = st.empty()
            image_placeholder = st.empty()
            text_placeholder = st.empty()
            response = ""
            code_response = ""

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
                    if event.data.type == "response.code_interpreter_call_code.delta":
                        code_response += event.data.delta
                        code_placeholder.code(code_response)
                    elif event.data.type == "response.image_generation_call.partial_image":
                        image = base64.b64decode(event.data.partial_image_b64)
                        image_placeholder.image(image)



prompt = st.chat_input(
    "Agent에게 질문해주세요. 이미지 업로드 가능",
    accept_file=True,
    file_type=[
        "txt",
        "jpg",
        "jpeg",
        "png",
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

#==================================== Side Bar =========================================

with st.sidebar:
    push = st.button("db 초기화 버튼")
    if push:
        asyncio.run(session.clear_session())
    st.write(asyncio.run(session.get_items()))