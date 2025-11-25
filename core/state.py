from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[List[Any], add_messages]
    screenshot: str
    items: List[Dict[str, Any]]
    goal: str
