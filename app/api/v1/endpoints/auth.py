import traceback

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from typing import Dict

# from app.services.auth_service import auth_service
# from app.schemas.auth import *
# from app.utils.user_storage import user_storage
# from app.dependencies import get_current_user, get_db
# from app.repositories import user_repository

from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session

# from app.models.user import User


router = APIRouter()


@router.get("/test/")
async def test():
    return {"message": "test"}
