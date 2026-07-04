"""
Disease Detection Models
"""

import enum
from sqlalchemy import String, Float, Integer, Text, Boolean, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin


class DiseaseSeverity(str, enum.Enum):
    none = "none"
    mild = "mild"
    moderate = "moderate"
    severe = "severe"
    critical = "critical"


class DiseaseReport(Base, TimestampMixin):
    """AI-powered disease detection report."""
    __tablename__ = "disease_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    farm_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("farms.id"), nullable=True, index=True)
    crop_cycle_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("crop_cycles.id"), nullable=True)

    # Image
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    image_key: Mapped[str | None] = mapped_column(String(500), nullable=True)  # S3 key

    # Detection results
    crop_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    disease_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    disease_scientific_name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    severity: Mapped[DiseaseSeverity] = mapped_column(SAEnum(DiseaseSeverity), default=DiseaseSeverity.none)
    affected_area_percent: Mapped[float | None] = mapped_column(Float, nullable=True)

    # AI Explanation (Explainable AI)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Treatment
    chemical_treatment: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    organic_treatment: Mapped[str | None] = mapped_column(Text, nullable=True)   # JSON
    prevention_tips: Mapped[str | None] = mapped_column(Text, nullable=True)     # JSON
    medicine_dosage: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_loss_percent: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Risk and alternatives
    risk_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    alternative_diagnosis: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON

    # Status
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    farmer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Processing
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ai_model_used: Mapped[str | None] = mapped_column(String(100), nullable=True)
    raw_ai_response: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="disease_reports")
    farm: Mapped["Farm | None"] = relationship("Farm", back_populates="disease_reports")
