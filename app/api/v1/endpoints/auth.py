import traceback

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from typing import Dict

# from app.services.auth_service import auth_service
# from app.schemas.auth import *
# from app.utils.user_storage import user_storage
from app.dependencies import get_db

# from app.repositories import user_repository

from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User


router = APIRouter()


@router.get("/user-exists", status_code=status.HTTP_200_OK)
async def test(db: Session = Depends(get_db), email: str = ""):
    try:
        user = db.query(User).filter(User.email.ilike(email)).first()
        if user:
            return {"message": "User exists", "user_exists": True, "data": user}
        else:
            return {"message": "User does not exist", "user_exists": False}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
