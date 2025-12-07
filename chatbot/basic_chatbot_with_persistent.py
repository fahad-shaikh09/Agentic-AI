from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
import os
from dotenv import load_dotenv
import chainlit as cl


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = os.getenv("BASE_URL")

client = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)

model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=client)

agent = Agent(name="chatbot-agent", model=model)

@cl.on_chat_start
async def start():

    await cl.Message(content="Hello! How can I assist you today?").send()

    
@cl.on_message
async def main(message: str):
    runner = await Runner.run(agent, input=message.content)
    await cl.Message(content=runner.final_output).send()
    
    