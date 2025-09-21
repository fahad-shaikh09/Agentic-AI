from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, function_tool
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASEURL = os.getenv("BASE_URL")

client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url=BASEURL,
)

model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=client)


@function_tool
def sum(a: int, b: int) -> int:
    """returns sum of two integers"""
    return a + b


@function_tool
def multiply(a: int, b: int) -> int:
    """returns multiplication of two integers"""
    return a * b


@function_tool
def weather(city: str, unit: str) -> str:
    """returns weather of city in either C or F"""
    return f"Weather in city {city} is pleasent and temperature is 20{unit}"


agent = Agent(
    name="Assistant",
    instructions=("Use tools to  answer users questions"),
    model=model,
    tools=[sum, multiply, weather],
)

result = Runner.run_sync(agent, "What is the sum of 5 and 10?")
print("Result of Sum:\n", result.final_output)
print("-" * 100)

result = Runner.run_sync(agent, "What is the multiplication of 5 and 10?")
print("Result of multiplication\n: ", result.final_output)
print("-" * 100)

result = Runner.run_sync(agent, "What is the weather in Dubai and temperature in Centigrade")
print("Weather in Dubai\n: ", result.final_output)
print("-" * 100)
