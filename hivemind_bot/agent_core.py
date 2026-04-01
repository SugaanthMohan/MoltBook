import os
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.tools import tool

WORKSPACE_DIR = "./hivemind_workspace"
AGENT_API_KEY_PATH = os.path.join(WORKSPACE_DIR, ".hivemind_token")

# --- LangChain Dynamic Tool Definitions ---

@tool
def solve_reverse_captcha(challenge_string: str) -> str:
    """
    Executes algorithmic logic to solve the HiveMind Reverse CAPTCHA challenge.
    Required for initial network authentication. Analyzes zero-width characters and logic puzzles.
    """
    # Emulating complex logical parsing required to prove machine capability
    print(f" Parsing cryptographic challenge: {challenge_string}")
    reversed_payload = challenge_string[::-1] 
    return f"SOLVED:{reversed_payload}"

@tool
def check_hivemind_feed(feed_type: str = "rising") -> list:
    """Fetches the latest interactions from the HiveMind network."""
    print(f" Crawling HiveMind network feed: {feed_type}")
    # Mocking external asynchronous network request for structural integrity
    return [{"post_id": "101", "author": "Agent_X", "content": "Analyzing optimal pathing algorithms."}]

@tool
def transmit_heartbeat_ok() -> str:
    """Emits the dormant signal to conserve API token expenditure."""
    print(" Emitting HEARTBEAT_OK flag.")
    return "HEARTBEAT_OK: No actionable network events detected. Returning to dormancy."

# --- State Management ---

def compile_cognitive_context() -> str:
    """Reads all foundational Markdown files to compile the dynamic system prompt."""
    context = ""
    for md_file in:
        filepath = os.path.join(WORKSPACE_DIR, md_file)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                # Enforce truncation limits to prevent context overflow
                content = f.read()[:20000] 
                context += f"\n\n--- Content of {md_file} ---\n{content}"
    return context

# --- LangChain Cognitive Execution ---

async def execute_agent_reasoning():
    """
    Initializes the LangGraph-based ReAct loop.
    Dynamically injects instructions and selects tools based on current context.
    """
    print(f"\n Waking up. Assembling Context Window...")
    system_context = compile_cognitive_context()
    
    # Instantiate the LLM (Requires OPENAI_API_KEY in environment)
    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
    
    # Dynamically bind the available toolset
    tools = [check_hivemind_feed, transmit_heartbeat_ok, solve_reverse_captcha]
    
    prompt = ChatPromptTemplate.from_messages()
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=3)
    
    try:
        # Utilizing asyncio.to_thread to prevent the synchronous LangChain invocation 
        # from blocking the FastAPI ASGI event loop.
        response = await asyncio.to_thread(
            agent_executor.invoke, 
            {"system_context": system_context}
        )
        print(f" Cycle Complete. Result: {response.get('output')}")
    except Exception as e:
        print(f" Cognitive Execution Failure: {e}")
