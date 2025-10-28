import traceback

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.utilities.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserSchema

router = APIRouter()


@router.get("/me")
async def profile(user: User = Depends(get_current_user)):
    if not user:
        return JSONResponse(
            {"message": "User not found"}, status_code=status.HTTP_404_NOT_FOUND
        )
    user_res = UserSchema.model_validate(user, from_attributes=True)
    return {"message": "User profile data", "data": user_res.model_dump()}
