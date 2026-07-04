"""
Chat, Market, Notification, Task, Analytics Models
"""

import enum
from datetime import date
from sqlalchemy import String, Float, Integer, Text, Boolean, Date, Enum as SAEnum, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin


# ─── AI Chat ──────────────────────────────────────────────────────────
class ChatSession(Base, TimestampMixin):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), default="New Conversation")
    language: Mapped[str] = mapped_column(String(10), default="en")
    context: Mapped[str | None] = mapped_column(Text, nullable=True)  # Farm/crop context JSON
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="chat_sessions")
    messages: Mapped[list["ChatMessage"]] = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", lazy="selectin")


class ChatMessage(Base, TimestampMixin):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)   # "user" | "assistant"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en")

    # Explainable AI fields
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    sources: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    is_voice: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")


# ─── Market Prices ────────────────────────────────────────────────────
class MarketPrice(Base, TimestampMixin):
    __tablename__ = "market_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    crop_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    market_name: Mapped[str] = mapped_column(String(200), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    price_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    min_price: Mapped[float] = mapped_column(Float, nullable=False)
    max_price: Mapped[float] = mapped_column(Float, nullable=False)
    modal_price: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="quintal")
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)


# ─── Government Schemes ───────────────────────────────────────────────
class GovernmentScheme(Base, TimestampMixin):
    __tablename__ = "government_schemes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    scheme_code: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True)
    authority: Mapped[str] = mapped_column(String(200), nullable=False)   # Central / State
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)  # None = all India
    category: Mapped[str] = mapped_column(String(100), nullable=False)   # insurance, subsidy, loan...
    description: Mapped[str] = mapped_column(Text, nullable=False)
    benefits: Mapped[str | None] = mapped_column(Text, nullable=True)     # JSON list
    eligibility: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list
    required_documents: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list
    application_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    max_benefit_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON


# ─── Notifications ────────────────────────────────────────────────────
class NotificationType(str, enum.Enum):
    disease_alert = "disease_alert"
    weather_alert = "weather_alert"
    task_reminder = "task_reminder"
    market_price = "market_price"
    scheme_deadline = "scheme_deadline"
    ai_recommendation = "ai_recommendation"
    system = "system"
    sos = "sos"


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[NotificationType] = mapped_column(SAEnum(NotificationType), default=NotificationType.system)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    action_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    data: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON payload

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")


# ─── Tasks ────────────────────────────────────────────────────────────
class TaskStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    skipped = "skipped"


class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    farm_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("farms.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(SAEnum(TaskStatus), default=TaskStatus.pending)
    priority: Mapped[TaskPriority] = mapped_column(SAEnum(TaskPriority), default=TaskPriority.medium)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)  # irrigation, fertilizer...
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="tasks")
    farm: Mapped["Farm | None"] = relationship("Farm", back_populates="tasks")


# ─── Expenses / Analytics ─────────────────────────────────────────────
class ExpenseCategory(str, enum.Enum):
    seeds = "seeds"
    fertilizer = "fertilizer"
    pesticide = "pesticide"
    labor = "labor"
    irrigation = "irrigation"
    equipment = "equipment"
    transport = "transport"
    other = "other"


class Expense(Base, TimestampMixin):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    farm_id: Mapped[int] = mapped_column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_cycle_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("crop_cycles.id"), nullable=True)
    category: Mapped[ExpenseCategory] = mapped_column(SAEnum(ExpenseCategory), default=ExpenseCategory.other)
    description: Mapped[str] = mapped_column(String(300), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    receipt_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    farm: Mapped["Farm"] = relationship("Farm", back_populates="expenses")


# ─── AI Recommendations ───────────────────────────────────────────────
class AIRecommendation(Base, TimestampMixin):
    __tablename__ = "ai_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    farm_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("farms.id"), nullable=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # crop, irrigation, fertilizer...

    # Explainable AI (mandatory)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    alternatives: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    risk_level: Mapped[str | None] = mapped_column(String(20), nullable=True)

    is_applied: Mapped[bool] = mapped_column(Boolean, default=False)
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False)
