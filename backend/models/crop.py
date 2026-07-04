"""
Crop & CropCycle Models
"""

import enum
from datetime import date
from sqlalchemy import String, Float, Integer, Text, Boolean, Date, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin


class CropSeason(str, enum.Enum):
    kharif = "kharif"       # June–November (monsoon)
    rabi = "rabi"           # November–April (winter)
    zaid = "zaid"           # April–June (summer)
    perennial = "perennial"


class CropStatus(str, enum.Enum):
    planned = "planned"
    sowing = "sowing"
    growing = "growing"
    flowering = "flowering"
    harvesting = "harvesting"
    harvested = "harvested"
    failed = "failed"


class Crop(Base, TimestampMixin):
    """Master list of crops (seeded data)."""
    __tablename__ = "crops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    local_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    scientific_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # cereal, vegetable, fruit...
    season: Mapped[CropSeason] = mapped_column(SAEnum(CropSeason), default=CropSeason.kharif)

    # Growing parameters
    water_requirement_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    growth_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ideal_temp_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    ideal_temp_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    ideal_ph_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    ideal_ph_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    ideal_rainfall_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    suitable_soils: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    avg_yield_per_acre: Mapped[float | None] = mapped_column(Float, nullable=True)  # quintals
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    common_diseases: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array

    # Relationships
    crop_cycles: Mapped[list["CropCycle"]] = relationship("CropCycle", back_populates="crop")

    def __repr__(self) -> str:
        return f"<Crop id={self.id} name={self.name}>"


class CropCycle(Base, TimestampMixin):
    """A single growing cycle of a crop on a farm/field."""
    __tablename__ = "crop_cycles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    farm_id: Mapped[int] = mapped_column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    field_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("fields.id"), nullable=True)
    crop_id: Mapped[int] = mapped_column(Integer, ForeignKey("crops.id"), nullable=False)

    # Timeline
    sowing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expected_harvest_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_harvest_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Details
    area_acres: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[CropStatus] = mapped_column(SAEnum(CropStatus), default=CropStatus.planned)
    season: Mapped[CropSeason] = mapped_column(SAEnum(CropSeason), default=CropSeason.kharif)
    variety: Mapped[str | None] = mapped_column(String(100), nullable=True)
    seed_quantity_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    fertilizer_used: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON

    # Yield
    expected_yield_quintals: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_yield_quintals: Mapped[float | None] = mapped_column(Float, nullable=True)
    selling_price_per_quintal: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_revenue: Mapped[float | None] = mapped_column(Float, nullable=True)

    # AI predictions
    ai_yield_prediction: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_yield_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    farm: Mapped["Farm"] = relationship("Farm", back_populates="crop_cycles")
    crop: Mapped["Crop"] = relationship("Crop", back_populates="crop_cycles")
    harvests: Mapped[list["Harvest"]] = relationship("Harvest", back_populates="crop_cycle")


class Harvest(Base, TimestampMixin):
    """Individual harvest event."""
    __tablename__ = "harvests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    crop_cycle_id: Mapped[int] = mapped_column(Integer, ForeignKey("crop_cycles.id", ondelete="CASCADE"), nullable=False)
    harvest_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity_quintals: Mapped[float] = mapped_column(Float, nullable=False)
    quality_grade: Mapped[str | None] = mapped_column(String(10), nullable=True)  # A, B, C
    selling_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    buyer_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    market_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    crop_cycle: Mapped["CropCycle"] = relationship("CropCycle", back_populates="harvests")
