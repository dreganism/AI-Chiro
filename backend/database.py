from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models import Base

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

try:
    Base.metadata.create_all(bind=engine)
except Exception as exc:  # pragma: no cover - defensive for cold starts
    print(f"Database bootstrap skipped: {exc}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
