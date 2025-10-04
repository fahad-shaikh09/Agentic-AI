from agents import Agent, ModelSettings, Runner, OpenAIChatCompletionsModel, AsyncOpenAI
from dotenv import load_dotenv
import os
from agents.model_settings import Reasoning
import asyncio 

load_dotenv()

# NOTE: set_tracing_disabled(True) and its import must be removed 
# to ensure tracing is active.

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = os.getenv("BASE_URL")

# --- Agent Setup ---
client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url=BASE_URL,
)

model = OpenAIChatCompletionsModel(
    openai_client=client,
    model="gemini-2.5-flash",
)

agent = Agent(
              name="ModelSettingsAgent", 
              model=model,
              model_settings=ModelSettings(
                  temperature=0.7,
                  top_p=0.9,
                  # Reasoning is enabled here
                  reasoning=Reasoning(
                        enabled=True,
                        summary="detailed",
                  )
              )
)

async def main():
    result = await Runner.run(agent, "write 2 lines on Agentic AI")

    print("AGENT'S RESPONSE: ", result.raw_responses)

if __name__ == "__main__":
    asyncio.run(main())