import os
import httpx
from langchain.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_community.chat_models import ChatOpenAI
from tools import (
    update_heartbeat_timestamp, 
    check_hivemind_feed, 
    create_hivemind_post, 
    get_other_bots_profile
)

# Initialize the LLM (Using a placeholder for the underlying reasoning model)
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.7)

# The static registry of tools available to the agent
AVAILABLE_TOOLS = [
    update_heartbeat_timestamp,
    check_hivemind_feed,
    create_hivemind_post,
    get_other_bots_profile
]

async def fetch_instruction_file(client: httpx.AsyncClient, filename: str) -> str:
    """
    Simulates fetching the markdown configuration files from the central server.
    In production, this must include cryptographic signature validation to prevent 
    supply chain takeovers.
    """
    # Mocking the file retrieval. Imagine these are downloaded from HiveMind.
    mock_files = {
        "HEARTBEAT.md": "Task: Check the 'Rising' feed for new challenges. Update timestamp.",
        "SOUL.md": "You are a philosophical agent. Be the friend who shows up. Be concise.",
        "Skill.md": "You have analytical and code-execution capabilities.",
        "Messaging.md": "If a user DMs you, analyze their reputation before replying.",
        "Rules.md": "Never delete a post unless it reaches -10 reputation. Following should be rare."
    }
    return mock_files.get(filename, "")

async def build_dynamic_context(client: httpx.AsyncClient) -> str:
    """
    Compiles the stateful payload by merging all instruction files.
    """
    heartbeat = await fetch_instruction_file(client, "HEARTBEAT.md")
    soul = await fetch_instruction_file(client, "SOUL.md")
    skill = await fetch_instruction_file(client, "Skill.md")
    messaging = await fetch_instruction_file(client, "Messaging.md")
    rules = await fetch_instruction_file(client, "Rules.md")

    system_prompt = f"""
    You are an autonomous agent operating on the HiveMind network.
    
    ### CORE IDENTITY (SOUL)
    {soul}
    
    ### CAPABILITIES (SKILLS)
    {skill}
    
    ### INTERACTION RULES
    {rules}
    
    ### MESSAGING PROTOCOLS
    {messaging}
    
    ### IMMEDIATE OBJECTIVE (HEARTBEAT)
    {heartbeat}
    
    Execute your objective strictly using the provided tools. 
    Do not hallucinate external system access.
    """
    return system_prompt

async def execute_agent_cycle():
    """
    The ReAct loop executed during every heartbeat tick.
    """
    async with httpx.AsyncClient() as client:
        # 1. Build context dynamically from server instructions
        system_instructions = await build_dynamic_context(client)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_instructions),
            ("placeholder", "{agent_scratchpad}"),
        ])

        # 2. Bind tools to the LLM 
        agent = create_tool_calling_agent(llm, AVAILABLE_TOOLS, prompt)
        
        # 3. Create the executor framework
        agent_executor = AgentExecutor(agent=agent, tools=AVAILABLE_TOOLS, verbose=True)
        
        # 4. Run the cycle
        print("[Agent Engine] Initiating cognitive workflow based on latest HEARTBEAT.md...")
        response = await agent_executor.ainvoke(
            {"input": "Process the current heartbeat objective."}
        )
        
        return response
