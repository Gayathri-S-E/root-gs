"""
User schemas — Auth, Registration, Profile
"""

from datetime import datetime
from typing import Optional
from pydantic import EmailStr, field_validator
from schemas.base import OurBaseModel
from models.user import UserRole


# ─── Auth ────────────────────────────────────────────────────────────
class UserRegister(OurBaseModel):
    email: EmailStr
    phone: Optional[str] = None
    full_name: str
    password: str
    role: UserRole = UserRole.farmer
    preferred_language: str = "en"

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserLogin(OurBaseModel):
    email: EmailStr
    password: str


class TokenResponse(OurBaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserOut"


class RefreshTokenRequest(OurBaseModel):
    refresh_token: str


class ForgotPasswordRequest(OurBaseModel):
    email: EmailStr


class ResetPasswordRequest(OurBaseModel):
    token: str
    new_password: str


# ─── User Output ─────────────────────────────────────────────────────
class FarmerProfileOut(OurBaseModel):
    id: int
    district: Optional[str] = None
    state: Optional[str] = None
    total_land_acres: Optional[float] = None
    farming_experience_years: Optional[int] = None
    primary_crops: Optional[str] = None
    bio: Optional[str] = None
    gemini_api_key: Optional[str] = None


class UserOut(OurBaseModel):
    id: int
    email: str
    phone: Optional[str] = None
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    profile_image: Optional[str] = None
    preferred_language: str
    created_at: datetime
    farmer_profile: Optional[FarmerProfileOut] = None


class UserUpdate(OurBaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    profile_image: Optional[str] = None
    preferred_language: Optional[str] = None


class FarmerProfileUpdate(OurBaseModel):
    district: Optional[str] = None
    state: Optional[str] = None
    pin_code: Optional[str] = None
    total_land_acres: Optional[float] = None
    farming_experience_years: Optional[int] = None
    primary_crops: Optional[str] = None
    bio: Optional[str] = None
    fcm_token: Optional[str] = None
    gemini_api_key: Optional[str] = None


class ChangePasswordRequest(OurBaseModel):
    current_password: str
    new_password: str
