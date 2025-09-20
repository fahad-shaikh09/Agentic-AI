from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI

import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL=os.getenv("BASE_URL")

# Initialize the client
client: AsyncOpenAI = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url=BASE_URL
    )

# Initialize the model
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client
)


# Create an agent
agent = Agent(name="HelloWorldAgent", model=model)

# Running the agent and definig the prompt
result = Runner.run_sync(starting_agent=agent, input="Write a 'Hello, World!' program in Python.")

# Print the result
response = print("Respnse:", result.final_output)

