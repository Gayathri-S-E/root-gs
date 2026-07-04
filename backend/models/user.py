"""
User Model — Users, roles, farmer profiles
"""

import enum
from sqlalchemy import String, Boolean, Enum as SAEnum, Text, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin


class UserRole(str, enum.Enum):
    farmer = "farmer"
    agriculture_officer = "agriculture_officer"
    agronomist = "agronomist"
    admin = "admin"
    researcher = "researcher"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.farmer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    profile_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)

    # Password reset
    reset_token: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    farmer_profile: Mapped["FarmerProfile | None"] = relationship(
        "FarmerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="selectin"
    )
    farms: Mapped[list["Farm"]] = relationship("Farm", back_populates="owner")
    chat_sessions: Mapped[list["ChatSession"]] = relationship("ChatSession", back_populates="user")
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="user")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="user")
    disease_reports: Mapped[list["DiseaseReport"]] = relationship("DiseaseReport", back_populates="user", foreign_keys="DiseaseReport.user_id")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"


class FarmerProfile(Base, TimestampMixin):
    """Extended profile for farmer role users."""
    __tablename__ = "farmer_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pin_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    total_land_acres: Mapped[float | None] = mapped_column(Float, nullable=True)
    farming_experience_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    primary_crops: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    aadhaar_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    bank_account: Mapped[str | None] = mapped_column(String(30), nullable=True)
    ifsc_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    fcm_token: Mapped[str | None] = mapped_column(String(500), nullable=True)  # Push notifications
    gemini_api_key: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="farmer_profile")
