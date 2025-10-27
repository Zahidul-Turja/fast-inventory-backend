from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Optional
from app.database import SessionLocal
from app.repositories import user_repository
from sqlalchemy.orm import session
from sqlalchemy.orm import Session

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
