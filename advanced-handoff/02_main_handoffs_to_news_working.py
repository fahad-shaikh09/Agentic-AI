from agents import (
    Agent,
    Runner,
    OpenAIChatCompletionsModel,
    AsyncOpenAI,
    function_tool,
    handoff,
    RunContextWrapper,
)
from dotenv import load_dotenv
import os
from pydantic import BaseModel

load_dotenv()
GEMENI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = os.getenv("BASE_URL")

client = AsyncOpenAI(base_url=BASE_URL, api_key=GEMENI_API_KEY)

model = OpenAIChatCompletionsModel(
    openai_client=client,
    model="gemini-2.5-flash",
)

# ---------------------------------------------------------------------
# Sub-agent 1: Weather
# ---------------------------------------------------------------------

@function_tool
def get_weather_tool(city: str) -> str:
    """Get the current weather for a given city."""
    return f"The current weather in {city} is sunny with a temperature of 25°C."

get_weather_agent = Agent(
    name="Weather Agent",
    model=model,
    instructions="""
    You must call the tool `get_weather_tool(city: str)` to get weather data.
    Always call the tool using the correct city name.
    After tool execution, respond with the tool's result directly.
    """,
    tools=[get_weather_tool],
    handoff_description="provides information about weather in some city.",
)

# ---------------------------------------------------------------------
# Sub-agent 2: News
# ---------------------------------------------------------------------

@function_tool
def get_news_tool(city: str) -> str:
    """Get the current news for a given city."""
    return f"The latest news in {city} is that the local team won their championship game."

get_news_agent = Agent(
    name="News Agent",
    model=model,
    instructions="""
    You are a helpful assistant that provides news about requested city.
    You must call the tool `get_news_tool(city: str)` to get news data.
    After tool execution, respond with the tool's result directly.
    """,
    tools=[get_news_tool],
    handoff_description="provides information about news in some city.",
)

# ---------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------

class WeatherRequest(BaseModel):
    topic: str = "weather"
    city: str

class NewsRequest(BaseModel):
    topic: str = "news"
    city: str

# ---------------------------------------------------------------------
# Handoff callbacks
# ---------------------------------------------------------------------

def transfer_to_weather_agent(ctx: RunContextWrapper, input_data: WeatherRequest):
    print("Handoff occurred to sub-agent. input_data:", input_data)

def transfer_to_news_agent(ctx: RunContextWrapper, input_data: NewsRequest):
    print("Handoff occurred to sub-agent. input_data:", input_data)

# ---------------------------------------------------------------------
# Tool to combine both sequentially (so we only call Runner once)
# ---------------------------------------------------------------------

@function_tool
async def get_weather_and_news(city: str) -> str:
    """Get both weather and news for a given city (sequential orchestration)."""
    # Run sub-agents sequentially
    weather_result = await Runner.run(get_weather_agent, f"Get weather in {city}")
    news_result = await Runner.run(get_news_agent, f"Get news in {city}")

    # Combine the outputs naturally
    return f"{weather_result.final_output}\n\n{news_result.final_output}"

# ---------------------------------------------------------------------
# Main Orchestrator Agent
# ---------------------------------------------------------------------

main_agent = Agent(
    name="Advanced Handoff Agent",
    model=model,
    instructions=""" 
    You are a helpful assistant that can delegate tasks to sub-agents.
    - If the user asks about weather, hand off to the Weather Agent.
    - If the user asks about news, hand off to the News Agent.
    - If the query contains both, call the tool `get_weather_and_news(city: str)` 
      to perform both actions sequentially and combine their results.
    Respond directly to the user with the final combined result.
    """,
    tools=[get_weather_and_news],
    handoffs=[
        handoff(
            agent=get_weather_agent,
            on_handoff=transfer_to_weather_agent,
            input_type=WeatherRequest,
        ),
        handoff(
            agent=get_news_agent,
            on_handoff=transfer_to_news_agent,
            input_type=NewsRequest,
        ),
    ],
)

# ---------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------

async def main():
    query = "What's the weather in Dubai and what's the latest news in Dubai?"
    result = await Runner.run(main_agent, query)
    print("Agent Response:\n", result.final_output)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
