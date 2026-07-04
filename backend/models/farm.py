"""
Farm & Field Models
"""

import enum
from sqlalchemy import String, Float, Integer, Text, Boolean, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.base import TimestampMixin


class SoilType(str, enum.Enum):
    clay = "clay"
    sandy = "sandy"
    loamy = "loamy"
    silty = "silty"
    peaty = "peaty"
    chalky = "chalky"
    clay_loam = "clay_loam"


class IrrigationType(str, enum.Enum):
    drip = "drip"
    sprinkler = "sprinkler"
    flood = "flood"
    furrow = "furrow"
    rainfed = "rainfed"
    none = "none"


class Farm(Base, TimestampMixin):
    __tablename__ = "farms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Location
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    village: Mapped[str | None] = mapped_column(String(100), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pin_code: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Farm details
    total_area_acres: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    soil_type: Mapped[SoilType] = mapped_column(SAEnum(SoilType), default=SoilType.loamy, nullable=False)
    irrigation_type: Mapped[IrrigationType] = mapped_column(SAEnum(IrrigationType), default=IrrigationType.rainfed, nullable=False)

    # Health & scoring
    health_score: Mapped[float] = mapped_column(Float, default=75.0, nullable=False)
    water_usage_score: Mapped[float] = mapped_column(Float, default=70.0, nullable=False)
    carbon_score: Mapped[float] = mapped_column(Float, default=65.0, nullable=False)

    # Images
    cover_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    images: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array of URLs

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="farms")
    fields: Mapped[list["Field"]] = relationship("Field", back_populates="farm", cascade="all, delete-orphan", lazy="selectin")
    crop_cycles: Mapped[list["CropCycle"]] = relationship("CropCycle", back_populates="farm")
    disease_reports: Mapped[list["DiseaseReport"]] = relationship("DiseaseReport", back_populates="farm")
    soil_reports: Mapped[list["SoilReport"]] = relationship("SoilReport", back_populates="farm")
    expenses: Mapped[list["Expense"]] = relationship("Expense", back_populates="farm")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="farm")

    def __repr__(self) -> str:
        return f"<Farm id={self.id} name={self.name}>"


class Field(Base, TimestampMixin):
    """Individual field/plot within a farm."""
    __tablename__ = "fields"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    farm_id: Mapped[int] = mapped_column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    area_acres: Mapped[float] = mapped_column(Float, nullable=False)
    soil_type: Mapped[SoilType] = mapped_column(SAEnum(SoilType), default=SoilType.loamy)
    coordinates: Mapped[str | None] = mapped_column(Text, nullable=True)  # GeoJSON polygon
    current_crop: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    farm: Mapped["Farm"] = relationship("Farm", back_populates="fields")


class SoilReport(Base, TimestampMixin):
    """Soil analysis report for a farm/field."""
    __tablename__ = "soil_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    farm_id: Mapped[int] = mapped_column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    field_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("fields.id"), nullable=True)

    # Soil parameters
    ph: Mapped[float | None] = mapped_column(Float, nullable=True)
    nitrogen: Mapped[float | None] = mapped_column(Float, nullable=True)        # kg/ha
    phosphorus: Mapped[float | None] = mapped_column(Float, nullable=True)      # kg/ha
    potassium: Mapped[float | None] = mapped_column(Float, nullable=True)       # kg/ha
    organic_matter: Mapped[float | None] = mapped_column(Float, nullable=True)  # %
    moisture: Mapped[float | None] = mapped_column(Float, nullable=True)        # %
    texture: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # AI recommendation
    ai_recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    suitable_crops: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array

    lab_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    sample_date: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Relationships
    farm: Mapped["Farm"] = relationship("Farm", back_populates="soil_reports")
