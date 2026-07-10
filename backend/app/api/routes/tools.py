from fastapi import APIRouter
from app.agents.tools import TOOL_REGISTRY

router = APIRouter()

@router.get("")
def tools():
    return [{"name": name, "description": fn.__doc__ or name.replace("_", " ").title()} for name, fn in TOOL_REGISTRY.items()]
