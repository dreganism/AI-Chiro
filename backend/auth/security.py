import re

from fastapi import HTTPException, status

from backend.config import settings

SPECIAL_PATTERN = re.compile(r"[!@#$%^&*(),.?\":{}|<>]")


def validate_password_strength(password: str) -> None:
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters long.",
        )
    if settings.PASSWORD_REQUIRE_SPECIAL and not SPECIAL_PATTERN.search(password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one special character.",
        )
