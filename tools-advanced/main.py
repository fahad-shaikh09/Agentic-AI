from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled, function_tool, RunContextWrapper
from dataclasses import dataclass
# from agents import StopAtTools
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


@dataclass
class UserInfo:
    is_admin: bool

user_info = UserInfo(is_admin=False) #HERE WE ARE MANAGING THE USER CONTEXT TO ADMIN / NON ADMIN WHICH WILL ENABLE / DISABLE TOOLS BASED ON THAT


def check_isadmin(ctx: RunContextWrapper[UserInfo], agent: Agent) -> bool:
    print(f" \n Checking User's context if User is Admin? : {ctx.context.is_admin} \n")
    return True if ctx.context.is_admin else False

@function_tool(is_enabled=check_isadmin)
def some_admin_tool():
    """A tool only for admins."""
    print("ADMIN TOOL'S RESPONSE: ")
    return "Admin tool executed."


# Define the agent with the tool
agent = Agent(
    name="Tools Advanced concepts",
    model=model,
    instructions="You are a helpful assistant. When a tool call is required, execute the tool and use its output in your response. Dont print tool's name in output",
    # tool_use_behavior=StopAtTools(stop_at_tool_names=["weather"]),
    tools=[weather, some_admin_tool],
)


# # Run the agent with the user context
result = Runner.run_sync(agent,
                         "Run an Admin level tool for me",
                         max_turns=5,
                         context=user_info
                         )

# Print the agent's response
print("AGENT'S RESPONSE: ", result.final_output)

