from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, function_tool, handoff, RunContextWrapper
from dotenv import load_dotenv
import os
from pydantic import BaseModel

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
    instructions="""You are a helpful assistant that provides news about requested city.""",
    tools=[get_news_tool],
    handoff_description="If the user asks for news, you need to answer user's query.",
)


class NewsRequest(BaseModel):
    city: str
    
    
def transfer_to_other_agent(ctx: RunContextWrapper, input_data: NewsRequest):
    print("Handoff occured to sub agent. input_data:", input_data)


main_agent = Agent(
    name="Advanced Handoff Agent",
    model=model,
    instructions="""You are a helpful assistant. 
    When a tool or agent call is required, execute the tool or agent and use its output in your response. 
    Dont print tool or agent's name in output""",
    handoffs=[handoff(agent=get_weather_agent, on_handoff=transfer_to_other_agent, input_type=NewsRequest), get_news_agent]
)



result = Runner.run_sync(main_agent, "hi, whats the weather in Dubai and whats the latest news there?")
print("Agent Response:", result.final_output)

