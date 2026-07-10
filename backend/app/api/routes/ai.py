import json
import time
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.agents.graph import CRMGraph
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas import AIChatRequest, AIChatResponse
from app.serialization import json_safe

router = APIRouter()

@router.post("/chat", response_model=AIChatResponse)
def chat(payload: AIChatRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return json_safe(CRMGraph(db).invoke(user.id, payload.message))

@router.post("/chat/stream")
def chat_stream(payload: AIChatRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    def events():
        for message in ["Intent Detection", "Entity Extraction", "Tool Selection", "Tool Execution", "Response Generation"]:
            yield f"data: {json.dumps({'type': 'status', 'message': message})}\n\n"
            time.sleep(0.03)
        result = json_safe(CRMGraph(db).invoke(user.id, payload.message))
        yield f"data: {json.dumps({'type': 'result', 'payload': result})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")
