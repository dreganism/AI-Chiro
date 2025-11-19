from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.auth.jwt_handler import decode_token
from backend.auth.utils import get_user_by_email
from backend.models import User

def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.split(" ")[1]
    payload = decode_token(token)
    if not payload or payload.get("sub") is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = get_user_by_email(db, payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
