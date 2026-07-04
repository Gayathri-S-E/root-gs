"""
Base Pydantic schema — OurBaseModel
All schemas in this project MUST extend OurBaseModel.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class OurBaseModel(BaseModel):
    """
    Base model for all Pydantic schemas.
    - orm_mode enabled (from_orm)
    - datetime serialized to ISO strings
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.isoformat()},
        populate_by_name=True,
    )
