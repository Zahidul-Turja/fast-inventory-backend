import traceback

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from typing import Dict
from sqlalchemy.orm import Session

# from app.services.auth_service import auth_service
# from app.utils.user_storage import user_storage
from app.repositories.user_repository import create_user, create_or_update_otp
from app.schemas.auth import *
from app.dependencies import get_db
from app.models.user import User, OTP

router = APIRouter()


@router.post("/user-exists", status_code=status.HTTP_200_OK)
async def test(request: UserCheckRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email.ilike(request.email)).first()
    if user:
        return {"message": "User exists", "user_exists": True, "data": user}
    else:
        return {"message": "User does not exist", "user_exists": False}


@router.post("/register", status_code=status.HTTP_200_OK)
async def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email.ilike(request.email)).first()
    if user:
        return {"message": "User already exists"}

    if request.password != request.confirm_password:
        return {"message": "Password and confirm password do not match"}

    try:
        user = {
            "name": request.name,
            "email": request.email,
            "password": request.password,
        }
        user = create_user(db, user)
        otp = create_or_update_otp(db, user)
        return {
            "message": "User created successfully",
            "data": {"name": user.name, "email": user.email},
        }
    except Exception as e:
        print(traceback.format_exc())
        return {"message": str(e)}


@router.post("/verify-otp", status_code=status.HTTP_200_OK)
async def verify_otp(request: UserVerifyOTPRequest, db: Session = Depends(get_db)):
    db_otp = db.query(OTP).filter(OTP.email == request.email).first()
    if db_otp and db_otp.otp == request.otp:
        db_user = db.query(User).filter(User.email == request.email).first()
        db_user.verified = True
        db.commit()
        db.refresh(db_user)
        user = UserDetailsResponse.model_validate(db_user, from_attributes=True)
        # user = UserDetailsResponse.from_orm(db_user)
        return {"message": "OTP verified successfully", "data": user}
    else:
        return {"message": "Invalid OTP"}
