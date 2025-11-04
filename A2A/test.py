from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model

llm = init_chat_model(model="gpt-4o")

response = llm.invoke("안녕")

print(response)
