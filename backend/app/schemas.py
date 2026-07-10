import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str = Field(min_length=8)

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserRead

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class HCPBase(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    specialty: str = Field(min_length=2, max_length=120)
    institution: str | None = None
    city: str | None = None
    email: EmailStr | None = None
    phone: str | None = None

class HCPCreate(HCPBase): ...
class HCPUpdate(HCPBase):
    name: str | None = None
    specialty: str | None = None

class HCPRead(HCPBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    sentiment_score: float
    last_contacted_at: datetime | None = None
    interaction_count: int = 0

class InteractionCreate(BaseModel):
    hcp_id: uuid.UUID | None = None
    hcp_name: str | None = None
    interaction_type: str = "in-person"
    occurred_at: datetime
    attendees: list[str] = Field(default_factory=list)
    topics_discussed: list[str] = Field(default_factory=list)
    materials_shared: list[str] = Field(default_factory=list)
    samples_distributed: list[str] = Field(default_factory=list)
    observed_sentiment: str = "neutral"
    outcome: str = Field(min_length=2)
    follow_up_action: str | None = None
    summary: str = Field(min_length=2)

    @field_validator("observed_sentiment")
    @classmethod
    def valid_sentiment(cls, value: str) -> str:
        allowed = {"positive", "neutral", "negative"}
        if value not in allowed:
            raise ValueError("observed_sentiment must be positive, neutral, or negative")
        return value

class InteractionUpdate(BaseModel):
    interaction_type: str | None = None
    occurred_at: datetime | None = None
    attendees: list[str] | None = None
    topics_discussed: list[str] | None = None
    materials_shared: list[str] | None = None
    samples_distributed: list[str] | None = None
    observed_sentiment: str | None = None
    outcome: str | None = None
    follow_up_action: str | None = None
    summary: str | None = None

class InteractionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    hcp_id: uuid.UUID
    interaction_type: str
    occurred_at: datetime
    attendees: list[str]
    topics_discussed: list[str]
    materials_shared: list[str]
    samples_distributed: list[str]
    observed_sentiment: str
    outcome: str
    follow_up_action: str | None
    summary: str
    hcp: HCPRead | None = None

class AIChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None

class AIChatResponse(BaseModel):
    intent: str
    response: str
    tool_used: str | None
    data: dict = Field(default_factory=dict)
    missing_fields: list[str] = Field(default_factory=list)
    confidence: float = 0.0

class FollowUpRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    hcp_id: uuid.UUID
    interaction_id: uuid.UUID
    due_at: datetime | None = None
    priority: str
    status: str
    action: str
    hcp: HCPRead | None = None

class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2)
    role: str | None = None

class SettingsRead(BaseModel):
    user: UserRead
    groq_model: str
    api_configured: bool

class DashboardMetrics(BaseModel):
    total_hcps: int
    todays_meetings: int
    pending_followups: int
    positive_sentiment_pct: float
    monthly_interactions: list[dict]
    recent_activity: list[dict]
    upcoming_meetings: list[dict]
