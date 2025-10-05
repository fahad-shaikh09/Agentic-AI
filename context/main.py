from agents import Agent, RunContextWrapper, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled, function_tool
from dotenv import load_dotenv
import os
from dataclasses import dataclass


set_tracing_disabled(True)
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

# Define a dataclass for user context
@dataclass 
class UserContext:
    user_name: str
    user_role: str
    user_experience: str


# Define a tool that uses the user context
@function_tool()
def greet_user(context: RunContextWrapper[UserContext]) -> str:
    # In a real application, this data might come from a database or user profile service
    return f"Welcome {context.context.user_name}, i see you are {context.context.user_role}, having {context.context.user_experience}"


# Define the instruction function used by Agent's instructions that uses the user context
def call_come_func(global_context: RunContextWrapper[UserContext], agent: Agent[Agent]) -> str:
    return f"You are a helpful assistant {agent.name}. Greet user {global_context.context.user_name} using the greet_user tool."


# Define the agent with the tool
agent = Agent(
    name="Context Management Agent",
    model=model,
    instructions=call_come_func,
    tools=[greet_user]
)

# Create a user context instance
user_context = UserContext(
        user_name="Alice",
        user_role="Software Engineer",
        user_experience="5 years in AI development"
    )


# # Run the agent with the user context
result = Runner.run_sync(agent,
                         "Hi",
                         context=user_context
                         )

# Print the agent's response
print("AGENT'S RESPONSE: ", result.final_output)

