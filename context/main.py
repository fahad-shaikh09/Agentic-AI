from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled, function_tool
from dotenv import load_dotenv
import os
from dataclasses import dataclass


set_tracing_disabled(True)
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = os.getenv("BASE_URL")

client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url=BASE_URL
)

model = OpenAIChatCompletionsModel(
    openai_client=client,
    model="gemini-2.5-flash",
)

@dataclass 
class UserContext:
    user_name: str
    user_role: str
    user_experience: str

# @function_tool()
# def get_user_context() -> UserContext:
#     # In a real application, this data might come from a database or user profile service
#     return UserContext(
#         user_name="Alice",
#         user_role="Software Engineer",
#         user_experience="5 years in AI development"
#     )

agent = Agent(
    name="ContextAgent",
    model=model,
)

user_context = UserContext(
        user_name="Alice",
        user_role="Software Engineer",
        user_experience="5 years in AI development"
    )



result = Runner.run_sync(agent,
                         "Do you know who am i?",
                         context=user_context
                         )

print("AGENT'S RESPONSE: ", result.final_output)

