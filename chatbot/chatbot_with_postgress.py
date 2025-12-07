import os
import uuid
from dotenv import load_dotenv
import chainlit as cl

from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel

# --- Persistence (SQLAlchemy async with Postgres) ---
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, DateTime, Text, func, select

# ----------------------------------------------------

load_dotenv()

POSTGRES_URL = os.getenv("POSTGRES_DATABASE_URL")
# Fix URL (remove leading psql ' ')
POSTGRES_URL = POSTGRES_URL.replace("psql ", "").replace("'", "")

DATABASE_URL = POSTGRES_URL.replace("postgresql://", "postgresql+asyncpg://")

Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: uuid.uuid4().hex)
    session_id = Column(String, index=True)
    role = Column(String)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


async_engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


# --- DB Helpers ---

async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def save_message(session_id: str, role: str, content: str):
    async with AsyncSessionLocal() as db:
        msg = Message(session_id=session_id, role=role, content=content)
        db.add(msg)
        await db.commit()

async def get_session_messages(session_id: str, limit: int | None = None):
    async with AsyncSessionLocal() as db:
        q = select(Message).where(Message.session_id == session_id).order_by(Message.created_at)
        result = await db.execute(q)
        msgs = [row[0] for row in result.fetchall()]
        if limit and len(msgs) > limit:
            msgs = msgs[-limit:]
        return msgs


# --- OpenAI Agent Setup ---

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = os.getenv("BASE_URL")

client = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)
model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=client)
agent = Agent(name="chatbot-agent", model=model)


# --- Runtime Session Tracking ---

ACTIVE_SESSION_ID = None


# --- Chainlit Events ---

@cl.on_chat_start
async def start():
    global ACTIVE_SESSION_ID

    await create_tables()

    ACTIVE_SESSION_ID = uuid.uuid4().hex
    await save_message(ACTIVE_SESSION_ID, "system", "Session started")

    await cl.Message(
        content="Hello! How can I assist you today?"
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    global ACTIVE_SESSION_ID

    user_text = message.content.strip()

    # ensure session exists
    if not ACTIVE_SESSION_ID:
        ACTIVE_SESSION_ID = uuid.uuid4().hex
        await save_message(ACTIVE_SESSION_ID, "system", "Session started")

    session_id = ACTIVE_SESSION_ID

    # save user message
    await save_message(session_id, "user", user_text)

    # load recent history (limit to protect tokens)
    msgs = await get_session_messages(session_id, limit=40)

    # build transcript
    transcript = []
    for m in msgs:
        r = m.role.upper()
        transcript.append(f"[{r}] {m.content}")

    transcript_text = "\n".join(transcript)

    # final prompt
    full_input = f"{transcript_text}\n\n[USER] {user_text}"

    # run agent
    try:
        runner = await Runner.run(agent, input=full_input)
        reply = getattr(runner, "final_output", str(runner))
    except Exception as e:
        reply = f"Error: {e}"

    # save reply to DB
    await save_message(session_id, "agent", reply)

    # send to UI
    await cl.Message(content=reply).send()
