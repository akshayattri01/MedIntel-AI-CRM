import json
from datetime import datetime, timezone

from app.agents.graph import CRMGraph
from app.schemas import InteractionCreate
from app.serialization import json_safe

def test_heuristic_extracts_doctor():
    graph = CRMGraph.__new__(CRMGraph)
    data = graph._heuristic_extract("I met Dr Sharma today. Discussed Product X. He liked efficacy.")
    assert data["doctor_name"] == "Dr Sharma"
    assert data["sentiment"] == "positive"

def test_greeting_does_not_fall_back_to_followup():
    graph = CRMGraph.__new__(CRMGraph)
    result = graph._heuristic_classify("hello")
    assert result.intent == "greeting"

def test_general_chat_does_not_use_crm_tool():
    graph = CRMGraph.__new__(CRMGraph)
    result = graph._heuristic_classify("what can you do")
    assert result.intent == "general_chat"

def test_log_interaction_without_details_still_requests_log_flow():
    graph = CRMGraph.__new__(CRMGraph)
    result = graph._heuristic_classify("Log interaction")
    assert result.intent == "log_interaction"

def test_normalized_entities_are_json_serializable():
    graph = CRMGraph.__new__(CRMGraph)
    entities = graph._normalize_entities({"meeting_date": "2026-07-10", "summary": "Met Dr Sharma"}, "Met Dr Sharma", "log_interaction")
    json.dumps(entities)
    assert isinstance(entities["occurred_at"], str)

def test_ai_response_shape_is_json_serializable():
    graph = CRMGraph.__new__(CRMGraph)
    final = {
        "intent": "log_interaction",
        "response": "Saved",
        "selected_tool": "log_interaction",
        "tool_result": {"ok": True, "occurred_at": datetime.now(timezone.utc)},
        "missing_fields": [],
        "confidence": 0.9,
    }
    payload = json_safe({
        "intent": final.get("intent", "unknown"),
        "response": final.get("response", ""),
        "tool_used": final.get("selected_tool"),
        "data": final.get("tool_result", {}),
        "missing_fields": final.get("missing_fields", []),
        "confidence": final.get("confidence", 0.0),
    })
    json.dumps(payload)
    assert isinstance(payload["data"]["occurred_at"], str)

def test_interaction_history_payload_encodes_datetime():
    payload = InteractionCreate(
        hcp_name="Dr Sharma",
        occurred_at=datetime.now(timezone.utc),
        outcome="Positive response",
        summary="Discussed Product X",
    )
    history_payload = json_safe(payload.model_dump(exclude={"hcp_id", "hcp_name"}))
    json.dumps(history_payload)
    assert isinstance(history_payload["occurred_at"], str)
