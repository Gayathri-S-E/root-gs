"""
Models __init__ — Export all models so Alembic can discover them.
"""

from models.base import Base, TimestampMixin, SoftDeleteMixin
from models.user import User, FarmerProfile, UserRole
from models.farm import Farm, Field, SoilReport, SoilType, IrrigationType
from models.crop import Crop, CropCycle, Harvest, CropSeason, CropStatus
from models.disease import DiseaseReport, DiseaseSeverity
from models.analytics import (
    ChatSession,
    ChatMessage,
    MarketPrice,
    GovernmentScheme,
    Notification,
    NotificationType,
    Task,
    TaskStatus,
    TaskPriority,
    Expense,
    ExpenseCategory,
    AIRecommendation,
)

__all__ = [
    "Base",
    "TimestampMixin",
    "SoftDeleteMixin",
    "User",
    "FarmerProfile",
    "UserRole",
    "Farm",
    "Field",
    "SoilReport",
    "SoilType",
    "IrrigationType",
    "Crop",
    "CropCycle",
    "Harvest",
    "CropSeason",
    "CropStatus",
    "DiseaseReport",
    "DiseaseSeverity",
    "ChatSession",
    "ChatMessage",
    "MarketPrice",
    "GovernmentScheme",
    "Notification",
    "NotificationType",
    "Task",
    "TaskStatus",
    "TaskPriority",
    "Expense",
    "ExpenseCategory",
    "AIRecommendation",
]
