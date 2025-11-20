from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.auth.utils import create_user, get_user_by_email, verify_password
from backend.auth.jwt_handler import create_access_token, create_refresh_token, decode_refresh_token
from backend.auth.security import validate_password_strength
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    validate_password_strength(password)
    if get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = create_user(db, email, password)
    return {"message": "User created successfully", "email": user.email}

@router.post("/login")
def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh")
def refresh_token(refresh_token: str = Form(...)):
    payload = decode_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    access_token = create_access_token(data={"sub": payload["sub"]})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout():
    return {"message": "Logged out. Please discard tokens on the client."}
