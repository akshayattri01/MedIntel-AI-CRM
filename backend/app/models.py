import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class TimestampMixin:
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

class User(TimestampMixin, Base):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(160))
    role: Mapped[str] = mapped_column(String(40), default="rep")
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    hcps: Mapped[list["HCP"]] = relationship(back_populates="owner")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user")

class RefreshToken(TimestampMixin, Base):
    __tablename__ = "refresh_tokens"
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    token: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    user: Mapped[User] = relationship(back_populates="refresh_tokens")

class HCP(TimestampMixin, Base):
    __tablename__ = "hcps"
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    specialty: Mapped[str] = mapped_column(String(120))
    institution: Mapped[str | None] = mapped_column(String(180))
    city: Mapped[str | None] = mapped_column(String(120))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(80))
    sentiment_score: Mapped[float] = mapped_column(Float, default=0.5)
    last_contacted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    owner: Mapped[User] = relationship(back_populates="hcps")
    interactions: Mapped[list["Interaction"]] = relationship(back_populates="hcp")
    __table_args__ = (Index("ix_hcps_owner_name", "owner_id", "name"),)

class Product(TimestampMixin, Base):
    __tablename__ = "products"
    name: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    therapy_area: Mapped[str | None] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text)

class Material(TimestampMixin, Base):
    __tablename__ = "materials"
    name: Mapped[str] = mapped_column(String(160), index=True)
    material_type: Mapped[str] = mapped_column(String(80))
    url: Mapped[str | None] = mapped_column(String(500))

class Sample(TimestampMixin, Base):
    __tablename__ = "samples"
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"))
    lot_number: Mapped[str | None] = mapped_column(String(80))
    quantity_available: Mapped[int] = mapped_column(Integer, default=0)
    product: Mapped[Product] = relationship()

class Interaction(TimestampMixin, Base):
    __tablename__ = "interactions"
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    hcp_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("hcps.id"), index=True)
    interaction_type: Mapped[str] = mapped_column(String(80))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    attendees: Mapped[list] = mapped_column(JSON, default=list)
    topics_discussed: Mapped[list] = mapped_column(JSON, default=list)
    materials_shared: Mapped[list] = mapped_column(JSON, default=list)
    samples_distributed: Mapped[list] = mapped_column(JSON, default=list)
    observed_sentiment: Mapped[str] = mapped_column(String(40), index=True)
    outcome: Mapped[str] = mapped_column(Text)
    follow_up_action: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str] = mapped_column(Text)
    hcp: Mapped[HCP] = relationship(back_populates="interactions")
    follow_ups: Mapped[list["FollowUp"]] = relationship(back_populates="interaction")
    __table_args__ = (Index("ix_interactions_owner_date", "owner_id", "occurred_at"),)

class FollowUp(TimestampMixin, Base):
    __tablename__ = "follow_ups"
    interaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("interactions.id"))
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    hcp_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("hcps.id"), index=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(30), default="pending")
    action: Mapped[str] = mapped_column(Text)
    interaction: Mapped[Interaction] = relationship(back_populates="follow_ups")
    hcp: Mapped[HCP] = relationship()

class InteractionHistory(TimestampMixin, Base):
    __tablename__ = "interaction_history"
    interaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("interactions.id"), index=True)
    actor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    event_type: Mapped[str] = mapped_column(String(80))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)

class AuditLog(TimestampMixin, Base):
    __tablename__ = "audit_logs"
    actor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    entity_type: Mapped[str] = mapped_column(String(80), index=True)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    action: Mapped[str] = mapped_column(String(80), index=True)
    meta: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
