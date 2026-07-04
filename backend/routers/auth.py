"""
Auth Router — Login, Register, Refresh, Password Reset
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from core.response import APIResponse
from core.dependencies import get_current_user
from models.user import User, FarmerProfile
from schemas.user import (
    UserRegister, UserLogin, TokenResponse, RefreshTokenRequest,
    ForgotPasswordRequest, ResetPasswordRequest, UserOut,
    UserUpdate, FarmerProfileUpdate, ChangePasswordRequest
)

router = APIRouter()


@router.post("/register", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        phone=payload.phone,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        preferred_language=payload.preferred_language,
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    await db.flush()

    # Auto-create farmer profile
    if payload.role == "farmer":
        profile = FarmerProfile(user_id=user.id)
        db.add(profile)

    await db.refresh(user)

    access = create_access_token(user.id, extra_data={"role": user.role})
    refresh = create_refresh_token(user.id)

    return APIResponse(
        success=True,
        message="Account created successfully! Welcome to ROOTGS 🌱",
        data=TokenResponse(
            access_token=access,
            refresh_token=refresh,
            user=UserOut.model_validate(user),
        ),
    )


@router.post("/login", response_model=APIResponse)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return JWT tokens."""
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    access = create_access_token(user.id, extra_data={"role": user.role})
    refresh = create_refresh_token(user.id)

    return APIResponse(
        success=True,
        message=f"Welcome back, {user.full_name}! 🌾",
        data=TokenResponse(
            access_token=access,
            refresh_token=refresh,
            user=UserOut.model_validate(user),
        ),
    )


@router.post("/refresh", response_model=APIResponse)
async def refresh_token(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Issue a new access token using a valid refresh token."""
    from jose import JWTError
    try:
        data = decode_token(payload.refresh_token)
        if data.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        user_id = data.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    access = create_access_token(user.id, extra_data={"role": user.role})

    return APIResponse(success=True, message="Token refreshed", data={"access_token": access, "token_type": "bearer"})


@router.get("/me", response_model=APIResponse)
async def get_me(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get current authenticated user's profile."""
    # Load farmer profile
    result = await db.execute(select(FarmerProfile).where(FarmerProfile.user_id == current_user.id))
    current_user.farmer_profile = result.scalar_one_or_none()

    return APIResponse(success=True, message="Profile loaded", data=UserOut.model_validate(current_user))


@router.put("/me", response_model=APIResponse)
async def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user's basic profile."""
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(current_user, field, value)
    await db.flush()

    return APIResponse(success=True, message="Profile updated", data=UserOut.model_validate(current_user))


@router.put("/me/farmer-profile", response_model=APIResponse)
async def update_farmer_profile(
    payload: FarmerProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update farmer-specific profile data."""
    result = await db.execute(select(FarmerProfile).where(FarmerProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()

    if not profile:
        profile = FarmerProfile(user_id=current_user.id)
        db.add(profile)

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(profile, field, value)

    await db.flush()
    return APIResponse(success=True, message="Farmer profile updated")


@router.post("/change-password", response_model=APIResponse)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change user password."""
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.hashed_password = hash_password(payload.new_password)
    await db.flush()
    return APIResponse(success=True, message="Password changed successfully")


@router.post("/forgot-password", response_model=APIResponse)
async def forgot_password(payload: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Send a password reset link (demo: returns token directly)."""
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if user:
        import secrets
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        await db.flush()
        # In production: send email with reset link

    return APIResponse(success=True, message="If that email exists, a reset link has been sent.")


@router.post("/reset-password", response_model=APIResponse)
async def reset_password(payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Reset password using token."""
    result = await db.execute(select(User).where(User.reset_token == payload.token))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user.hashed_password = hash_password(payload.new_password)
    user.reset_token = None
    await db.flush()

    return APIResponse(success=True, message="Password reset successfully. Please login.")
