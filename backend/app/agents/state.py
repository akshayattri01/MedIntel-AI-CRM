from typing import TypedDict

class AgentState(TypedDict, total=False):
    user_id: str
    message: str
    intent: str
    entities: dict
    selected_tool: str
    tool_result: dict
    response: str
    missing_fields: list[str]
    confidence: float
