from datetime import datetime, timedelta

from jose import JWTError, jwt

from backend.config import settings


def _create_token(data: dict, minutes: int, token_type: str) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=minutes)
    to_encode.update({"exp": expire, "token_type": token_type})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(data: dict) -> str:
    return _create_token(data, settings.ACCESS_TOKEN_EXPIRE_MINUTES, "access")


def create_refresh_token(data: dict) -> str:
    return _create_token(data, settings.REFRESH_TOKEN_EXPIRE_MINUTES, "refresh")


def decode_token(token: str, expected_type: str = "access"):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("token_type") != expected_type:
            raise JWTError("Invalid token type")
        return payload
    except JWTError:
        return None


def decode_refresh_token(token: str):
    return decode_token(token, expected_type="refresh")
