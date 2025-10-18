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
    return "Unread message: is there a discount policy?'"


inbox_monitor_agent: Agent = Agent(
    name="Inbox Monitor Agent",
    model=model,
    instructions="""
    You are a helpful Inbox Monitor Agent. Use the resources you have to assist users with their issues.
    Do not describe the tool; actually call it if needed. use handoff if required, dont just mention their names.
    """,
    tools=[get_unread_emails],
    handoff_description="You check unread emails and hand them off to the Router Agent for classification."
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
def billing_query_tool(issue_desc: str) -> str:
    """
    Handles billing and payment queries like refunds, invoices, or duplicate charges.
    """
    issue = issue_desc.lower()
    if "refund" in issue: 
        return "Your refund request is being processed. You’ll receive confirmation shortly."
    elif "invoice" in issue:
        return "Your invoice has been emailed to you."
    elif "duplicate charge" in issue:
        return "We have identified the duplicate charge and will refund it within 5-7 business days."
    else:
        return "For other billing issues, please contact our support team directly."
    
    
billing_agent: Agent = Agent(
    name="Billing Support Agent",
    instructions="""
    You assist users with all payment, refund, discount and invoice issues.
    When a billing issue is detected, use the available tool that processes billing queries.
    Pass the user's message or issue as an argument to that tool and return its result.
    """,
    model=model,
    tools=[billing_query_tool],
)

# Technical Support Agent
@function_tool
def tech_support_tool():
    return "Please try reinstalling the app or clear your cache."

tech_support_agent: Agent = Agent(
    name="Technical Support Agent",
    instructions="""
    You are a Technical Support Agent. Handle all app or system-related problems.
    When you detect a message mentioning errors, crashes, or issues,
    you MUST call the tool `tech_support_tool()` and return its output as your final response.
    Do not describe the tool; actually call it.""",
    model=model,
    tools=[tech_support_tool],
)


# General Assistant Agent

@function_tool
def faqs_tool():
    return "Our discount policy offers 10% off for first-time customers."

general_assistant_agent: Agent = Agent(
    name="General Assistant Agent",
    instructions="You are a General Assistant Agent. Help users with general inquiries.",
    model=model,
    tools=[faqs_tool],
)

# Setting up handoffs
inbox_monitor_agent.handoffs = [router_agent]
router_agent.handoffs = [billing_agent, tech_support_agent, general_assistant_agent]

# Running the Inbox Monitor Agent
result = Runner.run_sync(inbox_monitor_agent, input="Check unread emails and process any new requests.")

print("ACTIVE AGENT: ", result.last_agent.name)
print("AGENT'S RESPONSE: ", result.final_output)

