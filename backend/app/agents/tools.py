import uuid
from collections import Counter
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repositories.crm import InteractionRepository
from app.schemas import InteractionCreate, InteractionUpdate
from app.serialization import json_safe

def _coerce_datetime(value: datetime | str | None) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            return datetime.now(timezone.utc)
    return datetime.now(timezone.utc)

def log_interaction(db: Session, user_id: uuid.UUID, entities: dict) -> dict:
    required = ["doctor_name", "summary", "sentiment"]
    missing = [field for field in required if not entities.get(field)]
    if missing:
        return {"ok": False, "missing_fields": missing}
    payload = InteractionCreate(
        hcp_name=entities.get("doctor_name"),
        interaction_type=entities.get("interaction_type", "in-person"),
        occurred_at=_coerce_datetime(entities.get("occurred_at")),
        attendees=entities.get("attendees", []),
        topics_discussed=entities.get("products", []) + entities.get("topics", []),
        materials_shared=entities.get("materials", []),
        samples_distributed=entities.get("samples", []),
        observed_sentiment=entities.get("sentiment", "neutral"),
        outcome=entities.get("outcome", entities.get("summary", "Interaction logged")),
        follow_up_action=entities.get("follow_up"),
        summary=entities["summary"],
    )
    interaction = InteractionRepository(db).create(user_id, payload)
    return json_safe({
        "ok": True,
        "interaction_id": str(interaction.id),
        "doctor": interaction.hcp.name,
        "form": {
            "hcp_name": interaction.hcp.name,
            "interaction_type": interaction.interaction_type,
            "occurred_at": interaction.occurred_at.isoformat(),
            "attendees": interaction.attendees,
            "topics_discussed": interaction.topics_discussed,
            "materials_shared": interaction.materials_shared,
            "samples_distributed": interaction.samples_distributed,
            "observed_sentiment": interaction.observed_sentiment,
            "outcome": interaction.outcome,
            "follow_up_action": interaction.follow_up_action,
            "summary": interaction.summary,
        },
    })

def edit_interaction(db: Session, user_id: uuid.UUID, entities: dict) -> dict:
    interaction_id = entities.get("interaction_id")
    if not interaction_id:
        return {"ok": False, "missing_fields": ["interaction_id"]}
    repo = InteractionRepository(db)
    interaction = repo.get(user_id, uuid.UUID(interaction_id))
    if not interaction:
        return {"ok": False, "error": "Interaction not found"}
    payload = InteractionUpdate(**{k: v for k, v in entities.items() if k in InteractionUpdate.model_fields})
    repo.update(interaction, user_id, payload)
    return {"ok": True, "interaction_id": interaction_id}

def search_interactions(db: Session, user_id: uuid.UUID, entities: dict) -> dict:
    rows = InteractionRepository(db).list(user_id, q=entities.get("query") or entities.get("doctor_name"), limit=10)
    return json_safe({"ok": True, "results": [{"id": str(r.id), "doctor": r.hcp.name, "summary": r.summary, "date": r.occurred_at.isoformat()} for r in rows]})

def hcp_summary(db: Session, user_id: uuid.UUID, entities: dict) -> dict:
    doctor = entities.get("doctor_name")
    if not doctor:
        return {"ok": False, "missing_fields": ["doctor_name"]}
    rows = InteractionRepository(db).list(user_id, q=doctor, limit=5)
    products = Counter(topic for row in rows for topic in row.topics_discussed)
    objections = [r.outcome for r in rows if "concern" in r.outcome.lower() or "objection" in r.outcome.lower()]
    return json_safe({"ok": True, "doctor": doctor, "meetings": len(rows), "trends": [r.summary for r in rows[:3]], "objections": objections[:3], "opportunities": [f"Continue discussion on {name}" for name, _ in products.most_common(3)] or ["Schedule a discovery follow-up based on the latest meeting outcome"]})

def followup_planner(db: Session, user_id: uuid.UUID, entities: dict) -> dict:
    doctor = entities.get("doctor_name")
    rows = InteractionRepository(db).list(user_id, q=doctor, limit=1) if doctor else []
    sentiment = rows[0].observed_sentiment if rows else entities.get("sentiment", "neutral")
    priority = "high" if sentiment in {"positive", "negative"} else "medium"
    actions = []
    if rows:
        latest = rows[0]
        if latest.materials_shared:
            actions.append(f"Confirm whether {latest.hcp.name} reviewed {', '.join(latest.materials_shared)}")
        if latest.topics_discussed:
            actions.append(f"Prepare evidence for {', '.join(latest.topics_discussed[:2])}")
    actions.extend(["Schedule the next HCP touchpoint", "Record outcome immediately after the meeting"])
    return json_safe({"ok": True, "priority": priority, "actions": actions, "suggested_timing": entities.get("follow_up_date", "within 5 business days")})

def meeting_preparation(db: Session, user_id: uuid.UUID, entities: dict) -> dict:
    doctor = entities.get("doctor_name")
    if not doctor:
        return {"ok": False, "missing_fields": ["doctor_name"]}
    rows = InteractionRepository(db).list(user_id, q=doctor, limit=3)
    if not rows:
        return {"ok": True, "brief": f"No previous interactions found for {doctor}. Prepare discovery questions, product overview, and qualification notes."}
    last = rows[0]
    return json_safe({"ok": True, "brief": f"Last meeting with {last.hcp.name}: {last.summary}", "talking_points": last.topics_discussed, "materials_to_bring": last.materials_shared or ["Clinical evidence deck"], "risk_flags": [r.outcome for r in rows if r.observed_sentiment == "negative"]})

def next_best_action(db: Session, user_id: uuid.UUID, entities: dict) -> dict:
    doctor = entities.get("doctor_name")
    rows = InteractionRepository(db).list(user_id, q=doctor, limit=3)
    if not rows:
        return {"ok": True, "action": "Create an HCP profile and schedule an introductory meeting.", "priority": "medium"}
    latest = rows[0]
    if latest.observed_sentiment == "positive":
        action = "Send targeted clinical evidence and request a product demo slot."
        priority = "high"
    elif latest.observed_sentiment == "negative":
        action = "Schedule objection handling with a concise evidence summary."
        priority = "high"
    else:
        action = "Follow up with a focused question set and one relevant material."
        priority = "medium"
    return json_safe({"ok": True, "doctor": latest.hcp.name, "action": action, "priority": priority, "based_on": latest.summary})

def analytics_generator(db: Session, user_id: uuid.UUID, entities: dict) -> dict:
    metrics = InteractionRepository(db).metrics(user_id)
    return json_safe({"ok": True, "metrics": metrics})

TOOL_REGISTRY = {
    "log_interaction": log_interaction,
    "edit_interaction": edit_interaction,
    "search_interactions": search_interactions,
    "hcp_summary": hcp_summary,
    "followup_planner": followup_planner,
    "meeting_preparation": meeting_preparation,
    "next_best_action": next_best_action,
    "analytics_generator": analytics_generator,
}
