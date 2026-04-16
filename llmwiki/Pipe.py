from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

class WikiState(TypedDict):
    source_text: str
    relevant_slugs: List[str]
    current_page_content: str
    active_slug: str

llm = ChatOpenAI(model="gpt-4o")

def router_node(state: WikiState):
    """Step 1: Determine which wiki pages need updating."""
    schema = Path("meta/schema.json").read_text()
    prompt = f"Given this source: {state['source_text'][:2000]}\nAnd this wiki schema: {schema}\nReturn a JSON list of slugs to update."
    response = llm.invoke(prompt)
    # logic to parse JSON list
    return {"relevant_slugs": ["api-docs", "auth-flow"]} 

def synthesizer_node(state: WikiState):
    """Step 2: Incremental Synthesis (The Core Compilation Step)."""
    slug = state["active_slug"]
    page_path = Path(f"wiki/{slug}.md")
    existing_content = page_path.read_text() if page_path.exists() else ""
    
    prompt = f"""
    EXISTING WIKI PAGE: {existing_content}
    NEW SOURCE DATA: {state['source_text']}
    
    TASK: Rewrite the wiki page. 
    INVARIANT: Preserve all existing facts. Extend the page with new details. 
    Note contradictions. Return ONLY the new Markdown.
    """
    updated_content = llm.invoke(prompt).content
    page_path.write_text(updated_content)
    return {"current_page_content": updated_content}

# Graph Construction
workflow = StateGraph(WikiState)
workflow.add_node("route", router_node)
workflow.add_node("synthesize", synthesizer_node)

workflow.set_entry_point("route")
workflow.add_edge("route", "synthesize")
workflow.add_edge("synthesize", END)

app = workflow.compile()
