import os
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv()

model = init_chat_model(model='google_genai:gemini-3.1-flash-lite')

@tool
def get_weather(city: str) -> str:
    '''Get weather for a given city'''
    return f'It is always sunny in ${city}'

model_with_tool = model.bind_tools([get_weather])
result = model_with_tool.invoke('what is the weather in kuala lumpur?')

print(result)