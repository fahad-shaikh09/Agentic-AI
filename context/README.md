# Beginner-Level Summary: Context, Runner, and Tools in Agents

## 1. What is Context?
- Context is **shared information** about the user or session.
- Example: user name, role, preferences, or previous conversation.
- It can be used by **tools**, **agents**, and sometimes the **LLM**.

---

## 2. Where Context Exists

| Layer | Who sees it? | Purpose |
|-------|--------------|---------|
| **Runner** | Yes | Manages shared state during an agent run; can store user info, session data, etc. |
| **Tool (via RunContextWrapper)** | Yes | Accesses context to personalize actions or provide relevant results. |
| **LLM** | No, by default | Only sees what is included in the prompt (system/user messages). |

✅ Key: **Just giving context to Runner doesn’t automatically make LLM know it.**  

---

## 3. How to Make LLM See Context
1. **System instructions via `instructions` in Agent**
   ```python
   agent = Agent(
       name="MyAgent",
       model=model,
       instructions="You are talking to Alice, a software engineer."
   )


Persistent; every run uses this system prompt.

Pass system message in Runner.run_sync()

result = Runner.run_sync(agent, [
    {"role": "system", "content": "You are talking to Alice."},
    {"role": "user", "content": "Do you know who I am?"}
])


Dynamic; only applies to this run.

✅ Both approaches are valid, but instructions is better for persistent roles, system messages are better for one-off overrides.

4. How Context Reaches Tools

Tools get context via RunContextWrapper:

@function_tool()
async def greet(local_context: RunContextWrapper[UserContext]):
    return f"Hello, {local_context.context.username}"


Runner automatically passes context into RunContextWrapper.

Tools can read and modify context if needed.

5. Do we need to pass context both to Runner and tools?

Yes — it’s complementary, not redundant.

Runner: manages the global context for the run.

Tool: accesses that context via RunContextWrapper.

Tools cannot get context directly from anywhere else — Runner is the bridge.

6. Can we skip passing context to Runner and give it directly to tools?

Not normally.

Runner is the orchestrator — it controls tool invocation and context injection.

You can manually call tools with a RunContextWrapper for testing, but it bypasses the agent system.

Best practice: always pass context to Runner.

7. Key Things to Remember

Context exists separately from LLM prompts.

Runner context → available to all tools, but LLM won’t see it unless you include it in system/user messages.

Tools use RunContextWrapper to read/write context safely.

You can provide system instructions either:

Permanently via instructions in Agent, or

Temporarily via system message in Runner.run_sync().

Never try to bypass Runner to inject context — always let Runner handle it for proper orchestration.

For LLM personalization, inject context into prompts dynamically.

Runner + tools + LLM = three layers; understand which sees context and which doesn’t.

8. Mental Model (Simplified)
User Context --> Runner --> Tools (via RunContextWrapper)
                         \
                          --> LLM (only if injected into system/user prompt)


Runner = orchestrator

Tools = use context for personalized actions

LLM = only sees what you include in messages