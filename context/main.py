from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled
from dotenv import load_dotenv
import os


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

agent = Agent(
    name="ContextAgent",
    model=model,
)


result = Runner.run_sync(agent, "write 2 lines on Agentic AI")

print("AGENT'S RESPONSE: ", result.final_output)

