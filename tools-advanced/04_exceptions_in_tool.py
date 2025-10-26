from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled, function_tool
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
def get_weather(city) -> str:
    """Get the current weather for a given city."""
    try: 
       ...
    except Exception:
        raise Exception("Simulated API failure")
    except ValueError:
        raise ValueError("Simulated invalid input")
    except TimeoutError:
        raise TimeoutError("Simulated timeout") 
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
    
    
# Define the agent with the tool
agent = Agent(
    name="Tools Advanced concepts",
    model=model,
    instructions="You are a helpful assistant. When a tool call is required, execute the tool and use its output in your response. Dont print tool's name in output",
    tools=[get_weather],
)


# # Run the agent with the user context
result = Runner.run_sync(agent,
                         "Whats the weather in Dubai?",
                         max_turns=5,
                         )

# Print the agent's response
print("AGENT'S RESPONSE: ", result.final_output)

