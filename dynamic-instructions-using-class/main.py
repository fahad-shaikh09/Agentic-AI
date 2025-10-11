from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled,RunContextWrapper, function_tool
from dataclasses import dataclass
from dotenv import load_dotenv
import os
import asyncio 


set_tracing_disabled(True)

load_dotenv()
BASE_URL=os.getenv("BASE_URL")
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")


client = AsyncOpenAI(base_url=BASE_URL, api_key=GEMINI_API_KEY)

model = OpenAIChatCompletionsModel(
    openai_client=client,
    model="gemini-2.5-flash",
)

@function_tool()
def weather(city:str) -> str:
    return f"The weather in city {city} is sunny"

@dataclass
class UserInfo():
    name: str
    age: int
    location: str

async def main():

    def dyn_ins(context: RunContextWrapper[UserInfo], agent: Agent):
        
        return f"""
        You are a helpful assistant. The user information is as follows:
        Name: {user_info.name}
        Age: {user_info.age}
        Location: {user_info.location}
        Use this information to provide personalized responses.
        """
        
    agent = Agent(
        name="Dynamic Instruction Agent using Class as instructions",
        model=model,
        instructions=dyn_ins,
        tools=[weather]
    )
    
    user_info = UserInfo(name="Alice", age=30, location="New York")

    result = Runner.run_streamed(agent, "what is my name and what is your name", context=user_info)

    async for event in result.stream_events():
        print(event)
        
asyncio.run(main())

