from langgraph.graph import StateGraph, END
from typing import TypedDict, List

class WikiState(TypedDict):
    source_text: str
    relevant_slugs: List[str]
    active_slug: str

# Node 1: Routing - LLM determines which wiki pages are affected [4, 5]
def route_node(state: WikiState):
    # Reads meta/schema.json to see current "Page Universe"
    schema = Path("meta/schema.json").read_text()
    prompt = f"Source: {state['source_text'][:1000]}\nSchema: {schema}\nIdentify slugs to update."
    # LLM returns JSON list of slugs
    return {"relevant_slugs": ["api-docs", "auth-logic"]}

# Node 2: Synthesis - The "Upsert" operation [4, 5]
def synthesize_node(state: WikiState):
    slug = state["active_slug"]
    page_path = Path(f"wiki/{slug}.md")
    existing = page_path.read_text() if page_path.exists() else ""
    
    # Synthesis Invariant: Preserve all existing knowledge while extending [4, 5]
    prompt = f"EXISTING: {existing}\nNEW: {state['source_text']}\nPreserve and extend content."
    updated = llm.invoke(prompt).content
    page_path.write_text(updated)
    return state
