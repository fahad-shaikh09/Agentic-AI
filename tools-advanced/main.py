from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled, function_tool, StopAtTools
from dotenv import load_dotenv
import os


set_tracing_disabled(False)
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = os.getenv("BASE_URL")

# --- Agent Setup ---
client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url=BASE_URL
)

# Define the model
model = OpenAIChatCompletionsModel(
    openai_client=client,
    model="gemini-2.5-flash",
)

@function_tool
def weather(city) -> str:
    """Get the current weather for a given city."""
    # In a real implementation, this would call a weather API.
    return f"The current weather in {city} is sunny with a temperature of 25°C."

# Define the agent with the tool
agent = Agent(
    name="Tools Advanced concepts",
    model=model,
    instructions="You are a helpful assistant.",
    tool_use_behavior=StopAtTools(stop_at_tool_names=["weather"]),
    tools=[weather],
)


# # Run the agent with the user context
result = Runner.run_sync(agent,
                         "Whats weather in Dubai?",
                         max_turns=2
                         )

# Print the agent's response
print("AGENT'S RESPONSE: ", result.final_output)

