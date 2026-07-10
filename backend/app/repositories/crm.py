import uuid
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, selectinload
from app import models
from app.schemas import HCPCreate, HCPUpdate, InteractionCreate, InteractionUpdate
from app.serialization import json_safe

class HCPRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, owner_id: uuid.UUID, q: str | None = None):
        stmt = select(models.HCP).options(selectinload(models.HCP.interactions)).where(models.HCP.owner_id == owner_id, models.HCP.is_deleted.is_(False))
        if q:
            like = f"%{q}%"
            stmt = stmt.where(or_(models.HCP.name.ilike(like), models.HCP.specialty.ilike(like), models.HCP.institution.ilike(like)))
        return self.db.scalars(stmt.order_by(models.HCP.name)).all()

    def get(self, owner_id: uuid.UUID, hcp_id: uuid.UUID):
        return self.db.scalar(select(models.HCP).where(models.HCP.id == hcp_id, models.HCP.owner_id == owner_id, models.HCP.is_deleted.is_(False)))

    def by_name_or_create(self, owner_id: uuid.UUID, name: str):
        hcp = self.db.scalar(select(models.HCP).where(models.HCP.owner_id == owner_id, models.HCP.name.ilike(name), models.HCP.is_deleted.is_(False)))
        if hcp:
            return hcp
        hcp = models.HCP(owner_id=owner_id, name=name, specialty="General Medicine", institution=None, city=None, email=None, phone=None)
        self.db.add(hcp)
        self.db.flush()
        return hcp

    def history(self, owner_id: uuid.UUID, hcp_id: uuid.UUID):
        return self.db.scalars(
            select(models.Interaction)
            .options(selectinload(models.Interaction.hcp))
            .where(models.Interaction.owner_id == owner_id, models.Interaction.hcp_id == hcp_id, models.Interaction.is_deleted.is_(False))
            .order_by(models.Interaction.occurred_at.desc())
        ).all()

    def create(self, owner_id: uuid.UUID, payload: HCPCreate):
        hcp = models.HCP(owner_id=owner_id, **payload.model_dump())
        self.db.add(hcp)
        self.db.commit()
        self.db.refresh(hcp)
        return hcp

    def update(self, hcp: models.HCP, payload: HCPUpdate):
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(hcp, key, value)
        self.db.commit()
        self.db.refresh(hcp)
        return hcp

    def soft_delete(self, hcp: models.HCP):
        hcp.is_deleted = True
        hcp.deleted_at = datetime.now(timezone.utc)
        self.db.commit()

class InteractionRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, owner_id: uuid.UUID, q: str | None = None, sentiment: str | None = None, limit: int = 50, offset: int = 0):
        stmt = select(models.Interaction).options(selectinload(models.Interaction.hcp)).join(models.HCP).where(models.Interaction.owner_id == owner_id, models.Interaction.is_deleted.is_(False))
        if q:
            like = f"%{q}%"
            stmt = stmt.where(or_(models.HCP.name.ilike(like), models.Interaction.summary.ilike(like), models.Interaction.outcome.ilike(like)))
        if sentiment:
            stmt = stmt.where(models.Interaction.observed_sentiment == sentiment)
        return self.db.scalars(stmt.order_by(models.Interaction.occurred_at.desc()).limit(limit).offset(offset)).all()

    def get(self, owner_id: uuid.UUID, interaction_id: uuid.UUID):
        return self.db.scalar(select(models.Interaction).options(selectinload(models.Interaction.hcp)).where(models.Interaction.id == interaction_id, models.Interaction.owner_id == owner_id, models.Interaction.is_deleted.is_(False)))

    def create(self, owner_id: uuid.UUID, payload: InteractionCreate):
        hcp_repo = HCPRepository(self.db)
        if payload.hcp_id:
            hcp = hcp_repo.get(owner_id, payload.hcp_id)
            if not hcp:
                raise ValueError("HCP not found")
        elif payload.hcp_name:
            hcp = hcp_repo.by_name_or_create(owner_id, payload.hcp_name)
        else:
            raise ValueError("hcp_id or hcp_name is required")
        data = payload.model_dump(exclude={"hcp_id", "hcp_name"})
        history_payload = json_safe(data)
        interaction = models.Interaction(owner_id=owner_id, hcp_id=hcp.id, **data)
        hcp.last_contacted_at = payload.occurred_at
        hcp.sentiment_score = {"positive": 0.85, "neutral": 0.5, "negative": 0.2}.get(payload.observed_sentiment, 0.5)
        self.db.add(interaction)
        self.db.flush()
        if payload.follow_up_action:
            self.db.add(models.FollowUp(owner_id=owner_id, hcp_id=hcp.id, interaction_id=interaction.id, action=payload.follow_up_action, priority="medium"))
        self.db.add(models.InteractionHistory(interaction_id=interaction.id, actor_id=owner_id, event_type="created", payload=history_payload))
        self.db.commit()
        self.db.refresh(interaction)
        return interaction

    def update(self, interaction: models.Interaction, actor_id: uuid.UUID, payload: InteractionUpdate):
        changes = payload.model_dump(exclude_unset=True)
        for key, value in changes.items():
            setattr(interaction, key, value)
        self.db.add(models.InteractionHistory(interaction_id=interaction.id, actor_id=actor_id, event_type="updated", payload=json_safe(changes)))
        self.db.commit()
        self.db.refresh(interaction)
        return interaction

    def soft_delete(self, interaction: models.Interaction, actor_id: uuid.UUID):
        interaction.is_deleted = True
        interaction.deleted_at = datetime.now(timezone.utc)
        self.db.add(models.InteractionHistory(interaction_id=interaction.id, actor_id=actor_id, event_type="deleted", payload={}))
        self.db.commit()

    def metrics(self, owner_id: uuid.UUID):
        total_hcps = self.db.scalar(select(func.count()).select_from(models.HCP).where(models.HCP.owner_id == owner_id, models.HCP.is_deleted.is_(False))) or 0
        all_interactions = self.list(owner_id, limit=1000)
        interactions = all_interactions[:8]
        pending = self.db.scalar(select(func.count()).select_from(models.FollowUp).where(models.FollowUp.owner_id == owner_id, models.FollowUp.status == "pending", models.FollowUp.is_deleted.is_(False))) or 0
        positive = self.db.scalar(select(func.count()).select_from(models.Interaction).where(models.Interaction.owner_id == owner_id, models.Interaction.observed_sentiment == "positive", models.Interaction.is_deleted.is_(False))) or 0
        total_interactions = self.db.scalar(select(func.count()).select_from(models.Interaction).where(models.Interaction.owner_id == owner_id, models.Interaction.is_deleted.is_(False))) or 1
        today = datetime.now(timezone.utc).date()
        todays = sum(1 for item in all_interactions if item.occurred_at.date() == today)
        monthly = defaultdict(int)
        product_counter: Counter[str] = Counter()
        sentiment_counter: Counter[str] = Counter()
        for item in all_interactions:
            monthly[item.occurred_at.strftime("%b")] += 1
            sentiment_counter[item.observed_sentiment] += 1
            for topic in item.topics_discussed or []:
                product_counter[topic] += 1
        upcoming = self.db.scalars(
            select(models.FollowUp)
            .options(selectinload(models.FollowUp.hcp))
            .where(models.FollowUp.owner_id == owner_id, models.FollowUp.status == "pending", models.FollowUp.is_deleted.is_(False))
            .order_by(models.FollowUp.due_at.asc().nullslast())
            .limit(8)
        ).all()
        completed = self.db.scalar(select(func.count()).select_from(models.FollowUp).where(models.FollowUp.owner_id == owner_id, models.FollowUp.status == "completed", models.FollowUp.is_deleted.is_(False))) or 0
        total_followups = max(pending + completed, 1)
        return {
            "total_hcps": total_hcps,
            "todays_meetings": todays,
            "pending_followups": pending,
            "positive_sentiment_pct": round((positive / total_interactions) * 100, 1),
            "monthly_interactions": [{"month": month, "meetings": monthly[month]} for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]],
            "sentiment_breakdown": [{"name": key.title(), "value": value} for key, value in sentiment_counter.items()],
            "product_discussions": [{"name": key, "mentions": value} for key, value in product_counter.most_common(8)],
            "follow_up_completion": round((completed / total_followups) * 100, 1),
            "recent_activity": [{"doctor": i.hcp.name, "summary": i.summary, "sentiment": i.observed_sentiment, "date": i.occurred_at.isoformat()} for i in interactions],
            "upcoming_meetings": [{"id": str(f.id), "doctor": f.hcp.name if f.hcp else "HCP", "time": f.due_at.isoformat() if f.due_at else "Unscheduled", "type": f.action, "priority": f.priority} for f in upcoming],
        }

class FollowUpRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, owner_id: uuid.UUID, status: str | None = None):
        stmt = select(models.FollowUp).options(selectinload(models.FollowUp.hcp)).where(models.FollowUp.owner_id == owner_id, models.FollowUp.is_deleted.is_(False))
        if status:
            stmt = stmt.where(models.FollowUp.status == status)
        return self.db.scalars(stmt.order_by(models.FollowUp.due_at.asc().nullslast())).all()

    def complete(self, owner_id: uuid.UUID, follow_up_id: uuid.UUID):
        follow_up = self.db.scalar(select(models.FollowUp).where(models.FollowUp.id == follow_up_id, models.FollowUp.owner_id == owner_id, models.FollowUp.is_deleted.is_(False)))
        if not follow_up:
            return None
        follow_up.status = "completed"
        self.db.commit()
        self.db.refresh(follow_up)
        return follow_up
