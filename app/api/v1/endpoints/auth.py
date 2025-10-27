import traceback

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from typing import Dict
from sqlalchemy.orm import Session

# from app.services.auth_service import auth_service
# from app.utils.user_storage import user_storage
# from app.repositories import user_repository
from app.schemas.auth import *
from app.dependencies import get_db
from app.models.user import User

router = APIRouter()


@router.post("/user-exists", status_code=status.HTTP_200_OK)
async def test(request: UserCheckRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email.ilike(request.email)).first()
    if user:
        return {"message": "User exists", "user_exists": True, "data": user}
    else:
        return {"message": "User does not exist", "user_exists": False}
