from agents import Agent, AsyncOpenAI, function_tool, Runner, set_tracing_disabled, OpenAIChatCompletionsModel
from dotenv import load_dotenv
import os

load_dotenv()
set_tracing_disabled(False)

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
BASE_URL=os.getenv("BASE_URL")

client = AsyncOpenAI(
    base_url=BASE_URL,
    api_key=GEMINI_API_KEY
)

model = OpenAIChatCompletionsModel(
    openai_client=client,
    model="gemini-2.5-flash"
)

# Inbox Monitor Agent
@function_tool
def get_unread_emails():
    return "Unread message: 'My account was charged twice for the same order!'"


inbox_monitor_agent: Agent = Agent(
    name="Inbox Monitor Agent",
    model=model,
    instructions="You are a helpful Inbox Monitor Agent. Use the tools provided to assist users with their issues.",
    tools=[get_unread_emails],
    handoff_description="You check unread emails and hand them off to the Router Agent."
)

# Router Agent
router_agent: Agent = Agent(
    name="Router Agent",
    instructions="""You decide which agent should handle the issue.
    If message mentions payment, refund, invoice → handoff to Billing Support Agent.
    If message mentions error, app crash, not working → handoff to Technical Support Agent.
    Otherwise → handoff to General Assistant Agent.
    """,
    model=model,
    tools=[],
    handoff_description="Decide which agent to handoff to based on the user's issue"
)


# Billing Support Agent
@function_tool
def billing_query_tool():
    return "We've processed your refund for the duplicate charge"

billing_agent: Agent = Agent(
    name="Billing Support Agent",
    instructions="You are a Billing Support Agent. Help users with billing-related issues.",
    model=model,
    tools=[billing_query_tool],
)

# Technical Support Agent
@function_tool
def tech_support_tool():
    return "Please try reinstalling the app or clear your cache."

tech_support_agent: Agent = Agent(
    name="Technical Support Agent",
    instructions="You are a Technical Support Agent. Help users with technical issues.",
    model=model,
    tools=[tech_support_tool],
)


# General Assistant Agent
general_assistant_agent: Agent = Agent(
    name="General Assistant Agent",
    instructions="You are a General Assistant Agent. Help users with general inquiries.",
    model=model,
    tools=[],
)

# Setting up handoffs
inbox_monitor_agent.handoffs = [router_agent]
router_agent.handoffs = [billing_agent, tech_support_agent, general_assistant_agent]

# Running the Inbox Monitor Agent
result = Runner.run_sync(inbox_monitor_agent, input="Check unread emails and process any new requests.")

print("ACTIVE AGENT: ", result.last_agent.name)
print("AGENT'S RESPONSE: ", result.final_output)

