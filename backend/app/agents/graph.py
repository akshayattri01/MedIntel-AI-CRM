import json
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Literal

from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.agents.state import AgentState
from app.agents.tools import TOOL_REGISTRY
from app.config import settings
from app.serialization import json_safe

Intent = Literal[
    "greeting",
    "general_chat",
    "log_interaction",
    "edit_interaction",
    "search_interactions",
    "hcp_summary",
    "followup_planner",
    "meeting_preparation",
    "next_best_action",
    "analytics_generator",
]

TOOL_INTENTS = {
    "log_interaction",
    "edit_interaction",
    "search_interactions",
    "hcp_summary",
    "followup_planner",
    "meeting_preparation",
    "next_best_action",
    "analytics_generator",
}


class IntentClassification(BaseModel):
    intent: Intent
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class ExtractedCRMEntities(BaseModel):
    doctor_name: str | None = None
    products: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    materials: list[str] = Field(default_factory=list)
    samples: list[str] = Field(default_factory=list)
    meeting_date: str | None = None
    follow_up_date: str | None = None
    sentiment: Literal["positive", "neutral", "negative"] = "neutral"
    summary: str | None = None
    action_items: list[str] = Field(default_factory=list)
    follow_up: str | None = None
    outcome: str | None = None
    interaction_id: str | None = None
    interaction_type: str = "in-person"
    query: str | None = None


def _llm(temperature: float = 0.1) -> ChatGroq | None:
    if not settings.groq_api_key:
        return None
    return ChatGroq(model=settings.groq_model, api_key=settings.groq_api_key, temperature=temperature)


class CRMGraph:
    def __init__(self, db: Session):
        self.db = db
        graph = StateGraph(AgentState)
        graph.add_node("intent_detection", self.intent_detection)
        graph.add_node("entity_extraction", self.entity_extraction)
        graph.add_node("tool_selection", self.tool_selection)
        graph.add_node("execute_tool", self.execute_tool)
        graph.add_node("response_generation", self.response_generation)
        graph.set_entry_point("intent_detection")
        graph.add_edge("intent_detection", "entity_extraction")
        graph.add_edge("entity_extraction", "tool_selection")
        graph.add_edge("tool_selection", "execute_tool")
        graph.add_edge("execute_tool", "response_generation")
        graph.add_edge("response_generation", END)
        self.graph = graph.compile()

    def intent_detection(self, state: AgentState) -> AgentState:
        message = state["message"].strip()
        classification = self._classify_intent(message)
        return {**state, "intent": classification.intent, "confidence": classification.confidence}

    def entity_extraction(self, state: AgentState) -> AgentState:
        intent = state.get("intent", "general_chat")
        message = state["message"].strip()
        if intent not in TOOL_INTENTS:
            return {**state, "entities": {}}

        llm = _llm()
        if llm:
            structured = llm.with_structured_output(ExtractedCRMEntities)
            extracted = structured.invoke(
                "Extract healthcare CRM fields from this message. "
                "Use null or empty arrays for missing values. "
                "Return concise action_items and summary. "
                f"Intent: {intent}\nMessage: {message}"
            ).model_dump()
        else:
            extracted = self._heuristic_extract(message)

        extracted = self._normalize_entities(extracted, message, intent)
        return {**state, "entities": extracted}

    def tool_selection(self, state: AgentState) -> AgentState:
        intent = state.get("intent", "general_chat")
        selected_tool = intent if intent in TOOL_REGISTRY else None
        return {**state, "selected_tool": selected_tool}

    def execute_tool(self, state: AgentState) -> AgentState:
        selected_tool = state.get("selected_tool")
        if not selected_tool:
            return {**state, "tool_result": {}, "missing_fields": []}

        tool = TOOL_REGISTRY[selected_tool]
        result = json_safe(tool(self.db, uuid.UUID(state["user_id"]), state.get("entities", {})))
        return {**state, "tool_result": result, "missing_fields": result.get("missing_fields", [])}

    def response_generation(self, state: AgentState) -> AgentState:
        intent = state.get("intent", "general_chat")
        message = state["message"].strip()
        if intent == "greeting":
            response = self._greeting_response()
        elif intent == "general_chat":
            response = self._general_chat_response(message)
        elif state.get("missing_fields"):
            response = self._missing_fields_response(intent, state["missing_fields"])
        else:
            response = self._tool_response(state)
        return {**state, "response": response}

    def invoke(self, user_id: uuid.UUID, message: str) -> dict:
        final = self.graph.invoke({"user_id": str(user_id), "message": message})
        return json_safe({
            "intent": final.get("intent", "unknown"),
            "response": final.get("response", ""),
            "tool_used": final.get("selected_tool"),
            "data": final.get("tool_result", {}),
            "missing_fields": final.get("missing_fields", []),
            "confidence": final.get("confidence", 0.0),
        })

    def _classify_intent(self, message: str) -> IntentClassification:
        llm = _llm()
        if llm:
            structured = llm.with_structured_output(IntentClassification)
            return structured.invoke(
                "Classify this user message for a healthcare CRM AI assistant.\n"
                "Return only one intent from: greeting, general_chat, log_interaction, edit_interaction, "
                "search_interactions, hcp_summary, followup_planner, meeting_preparation, "
                "next_best_action, analytics_generator.\n"
                "Use greeting for hello/hi/opening messages. "
                "Use general_chat for thanks, bye, help, who are you, what can you do, or non-CRM questions. "
                "Only choose CRM tool intents when the user clearly requests CRM work.\n"
                f"Message: {message}"
            )
        return self._heuristic_classify(message)

    def _heuristic_classify(self, message: str) -> IntentClassification:
        text = message.lower().strip()
        if re.fullmatch(r"(hi|hello|hey|good morning|good afternoon|good evening)[!. ]*", text):
            return IntentClassification(intent="greeting", confidence=0.9)
        if re.search(r"\b(thanks|thank you|bye|help|who are you|what can you do|explain yourself)\b", text):
            return IntentClassification(intent="general_chat", confidence=0.85)
        if re.search(r"\blog\s+(an\s+)?interaction\b|\b(met|visited|discussed|shared|sampled|logged)\b", text):
            return IntentClassification(intent="log_interaction", confidence=0.78)
        if re.search(r"\b(edit|update|change|correct)\b", text):
            return IntentClassification(intent="edit_interaction", confidence=0.72)
        if re.search(r"\b(prepare|prep|brief)\b", text):
            return IntentClassification(intent="meeting_preparation", confidence=0.75)
        if re.search(r"\b(next best|recommend|suggest next|next action)\b", text):
            return IntentClassification(intent="next_best_action", confidence=0.75)
        if re.search(r"\b(search|find|show|list)\b", text):
            return IntentClassification(intent="search_interactions", confidence=0.72)
        if re.search(r"\b(summary|summarize|recap)\b", text):
            return IntentClassification(intent="hcp_summary", confidence=0.72)
        if re.search(r"\b(analytics|dashboard|metrics|trend)\b", text):
            return IntentClassification(intent="analytics_generator", confidence=0.78)
        if re.search(r"\b(follow[- ]?up|plan)\b", text):
            return IntentClassification(intent="followup_planner", confidence=0.7)
        return IntentClassification(intent="general_chat", confidence=0.65)

    def _heuristic_extract(self, message: str) -> dict:
        doctor = None
        match = re.search(r"\bDr\.?\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)", message)
        if match:
            doctor = "Dr " + match.group(1)

        sentiment = "positive" if re.search(r"liked|positive|interested|good|great|agreed|requested", message, re.I) else "negative" if re.search(r"concern|objection|not interested|poor|negative|declined", message, re.I) else "neutral"
        materials = re.findall(r"\b(?:brochure|deck|study|leaflet|paper|material|literature|clinical evidence)s?\b", message, re.I)
        products = re.findall(r"\bProduct\s+[A-Z0-9]+\b", message)
        samples = re.findall(r"\b\d+\s+(?:samples?|starter packs?)\b", message, re.I)
        follow_up = self._extract_follow_up_text(message)

        return {
            "doctor_name": doctor,
            "products": list(dict.fromkeys(products)),
            "topics": self._extract_topics(message, products),
            "materials": list(dict.fromkeys(m.title() for m in materials)),
            "samples": samples,
            "meeting_date": self._extract_relative_date(message, default_today=True),
            "follow_up_date": self._extract_relative_date(follow_up or message, default_today=False),
            "sentiment": sentiment,
            "summary": message.strip(),
            "action_items": [follow_up] if follow_up else [],
            "follow_up": follow_up,
            "outcome": message.strip(),
            "interaction_type": "in-person",
        }

    def _normalize_entities(self, entities: dict, message: str, intent: str) -> dict:
        normalized = dict(entities)
        if intent == "search_interactions":
            normalized["query"] = normalized.get("query") or message
        if normalized.get("meeting_date") and not normalized.get("occurred_at"):
            normalized["occurred_at"] = self._parse_date(normalized["meeting_date"]).isoformat()
        if normalized.get("action_items") and not normalized.get("follow_up"):
            normalized["follow_up"] = "; ".join(normalized["action_items"])
        if not normalized.get("summary") and intent == "log_interaction":
            normalized["summary"] = message
        return normalized

    def _general_chat_response(self, message: str) -> str:
        llm = _llm(temperature=0.3)
        if llm:
            result = llm.invoke(
                "You are the MedIntel AI CRM Assistant. Reply naturally and helpfully. "
                "Do not claim you executed CRM tools unless asked for CRM work. "
                "Keep the response concise.\n"
                f"User: {message}"
            )
            return str(result.content)
        text = message.lower()
        if "thank" in text:
            return "You're welcome. I am here whenever you need help with CRM follow-ups, HCP summaries, or analytics."
        if "bye" in text:
            return "Goodbye. Have a productive day."
        return (
            "I'm your MedIntel AI CRM Assistant. I can help log HCP interactions, search CRM records, "
            "summarize meetings, plan follow-ups, prepare for visits, explain analytics, and suggest next best actions."
        )

    def _greeting_response(self) -> str:
        return (
            "Hello! I'm your MedIntel AI CRM Assistant.\n\n"
            "I can help you with:\n\n"
            "- Logging HCP interactions\n"
            "- Searching CRM records\n"
            "- Meeting summaries\n"
            "- Follow-up planning\n"
            "- Analytics\n"
            "- Next Best Actions\n\n"
            "How can I help today?"
        )

    def _missing_fields_response(self, intent: str, missing_fields: list[str]) -> str:
        labels = {
            "doctor_name": "Which doctor or HCP is this about?",
            "summary": "What happened during the interaction?",
            "sentiment": "What was the doctor's sentiment: positive, neutral, or negative?",
            "interaction_id": "Which interaction should I update?",
        }
        questions = [labels.get(field, f"Please provide {field.replace('_', ' ')}.") for field in missing_fields]
        prefix = {
            "log_interaction": "Sure. I can log that interaction.",
            "hcp_summary": "Sure. I can summarize the HCP history.",
            "meeting_preparation": "Sure. I can prepare a meeting brief.",
            "edit_interaction": "Sure. I can update that record.",
        }.get(intent, "Sure. I can help with that.")
        return f"{prefix}\n\n{questions[0]}"

    def _tool_response(self, state: AgentState) -> str:
        result = state.get("tool_result", {})
        if not result.get("ok"):
            return result.get("error", "I could not complete that request. Please share a little more detail.")

        llm = _llm(temperature=0.2)
        if llm:
            generated = llm.invoke(
                "Write a polished enterprise healthcare CRM assistant response based on this tool result. "
                "Do not mention internal intent names, tool names, JSON, or implementation details. "
                "Use concise sections and practical next actions when useful.\n"
                f"User message: {state['message']}\n"
                f"Tool result: {json.dumps(result)}"
            )
            return str(generated.content)

        return self._format_tool_response(state.get("intent", "general_chat"), result)

    def _format_tool_response(self, intent: str, result: dict) -> str:
        if intent == "log_interaction":
            return (
                f"Interaction logged for {result.get('doctor', 'the HCP')}.\n\n"
                "Summary\n"
                f"- {result.get('form', {}).get('summary', 'The interaction details were captured.')}\n\n"
                "Recommended next action\n"
                "- Review the follow-up action and schedule the next touchpoint."
            )
        if intent == "search_interactions":
            rows = result.get("results", [])
            if not rows:
                return "I did not find matching CRM interactions. Try a doctor name, product, topic, or sentiment."
            lines = [f"- {row['doctor']}: {row['summary']}" for row in rows[:5]]
            return f"I found {len(rows)} matching interaction record(s).\n\n" + "\n".join(lines)
        if intent == "hcp_summary":
            trends = result.get("trends", [])
            lines = "\n".join(f"- {item}" for item in trends) if trends else "- No recent interaction trends found."
            return (
                f"I found {result.get('meetings', 0)} previous interaction(s) with {result.get('doctor', 'this HCP')}.\n\n"
                f"Summary\n{lines}\n\n"
                f"Recommended next action\n- {result.get('opportunities', ['Schedule a focused follow-up.'])[0]}"
            )
        if intent == "followup_planner":
            actions = "\n".join(f"- {action}" for action in result.get("actions", []))
            return (
                f"Follow-up plan created with {result.get('priority', 'medium')} priority.\n\n"
                f"Action plan\n{actions}\n\n"
                f"Suggested timing\n- {result.get('suggested_timing', 'within 5 business days')}"
            )
        if intent == "meeting_preparation":
            points = "\n".join(f"- {point}" for point in result.get("talking_points", []))
            return f"Meeting brief\n\n{result.get('brief', 'Prepare discovery questions and relevant clinical materials.')}\n\nTalking points\n{points or '- Confirm objectives and decision criteria.'}"
        if intent == "next_best_action":
            return (
                f"Recommended next best action\n\n- {result.get('action', 'Schedule a focused follow-up.')}\n\n"
                f"Priority: {result.get('priority', 'medium')}"
            )
        if intent == "analytics_generator":
            return "I generated the latest CRM analytics. Review the dashboard metrics for interaction trends, sentiment mix, and follow-up performance."
        return "Done."

    def _extract_topics(self, message: str, products: list[str]) -> list[str]:
        topics = []
        if re.search(r"\befficacy\b", message, re.I):
            topics.append("efficacy")
        if re.search(r"\bsafety\b", message, re.I):
            topics.append("safety")
        if re.search(r"\bpricing|cost\b", message, re.I):
            topics.append("pricing")
        return list(dict.fromkeys(products + topics))

    def _extract_follow_up_text(self, message: str) -> str | None:
        match = re.search(r"(follow[- ]?up[^.]*|next week[^.]*|next month[^.]*)", message, re.I)
        return match.group(1).strip() if match else None

    def _extract_relative_date(self, text: str, default_today: bool) -> str | None:
        lowered = text.lower()
        if "tomorrow" in lowered:
            return (datetime.now(timezone.utc) + timedelta(days=1)).date().isoformat()
        if "next week" in lowered:
            return (datetime.now(timezone.utc) + timedelta(days=7)).date().isoformat()
        if "today" in lowered:
            return datetime.now(timezone.utc).date().isoformat()
        return datetime.now(timezone.utc).date().isoformat() if default_today else None

    def _parse_date(self, value: str) -> datetime:
        try:
            return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
        except ValueError:
            return datetime.now(timezone.utc)
