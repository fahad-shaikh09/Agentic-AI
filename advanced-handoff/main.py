from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, function_tool
from dotenv import load_dotenv
import os


load_dotenv()
GEMENI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = os.getenv("BASE_URL")

client = AsyncOpenAI(
    base_url=BASE_URL,
    api_key=GEMENI_API_KEY
)

model = OpenAIChatCompletionsModel(
    openai_client=client,
    model="gemini-2.5-flash",
)

@function_tool
def get_weather_tool(city: str) -> str:
    """Get the current weather for a given city."""
    # In a real implementation, this would call a weather API.
    return f"The current weather in {city} is sunny with a temperature of 25°C."

get_weather_agent = Agent(
    name="Weather Agent",
    model=model,
    instructions="""You are a helpful assistant that provides weather information. 
    When asked about the weather in a city, respond with the current weather conditions.""",
    tools=[get_weather_tool],
    handoff_description="If the user asks for the weather, you need to answer user's query.",
)



@function_tool
def get_news_tool(city: str) -> str:
    """Get the current weather for a given city."""
    # In a real implementation, this would call a weather API.
    return f"The latest news in {city} is that the local team won their championship game."

get_news_agent = Agent(
    name="News Agent",
    model=model,
    instructions="""You are a helpful assistant that provides news information.""",
    tools=[get_news_tool],
    handoff_description="If the user asks for news, you need to answer user's query.",
)




main_agent = Agent(
    name="Advanced Handoff Agent",
    model=model,
    instructions="""You are a helpful assistant. 
    When a tool call is required, execute the tool and use its output in your response. 
    Dont print tool's name in output""",
    handoffs=[get_weather_agent, get_news_agent],
)


# main_agent.handoffs = [get_weather_agent, get_news_agent]

result = Runner.run_sync(main_agent, "hi, whats the weather in new york?")
print("Agent Response:", result.final_output)

