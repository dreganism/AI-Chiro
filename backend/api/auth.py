from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.auth.utils import create_user, get_user_by_email, verify_password
from backend.auth.jwt_handler import create_access_token
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
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
    
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=60)
    )
    return {"access_token": access_token, "token_type": "bearer"}
