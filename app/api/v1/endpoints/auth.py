import traceback
import random

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.requests import Request
from typing import Dict
from sqlalchemy.orm import Session

# from app.services.auth_service import auth_service
# from app.utils.user_storage import user_storage
from app.repositories.user_repository import (
    create_user,
    create_or_update_otp,
    authenticate_user,
)
from app.schemas.auth import *
from app.schemas.user_schema import UserSchema
from app.dependencies import get_db
from app.models.user_model import User, OTP
from app.utilities.auth import create_access_token, get_current_user
from app.core.config import settings

router = APIRouter()


# Test protected route
@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    # current_user is automatically attached, just like request.user in DRF
    return {"user": current_user.email, "message": "Protected data"}


@router.post("/user-exists", status_code=status.HTTP_200_OK)
async def user_exists(request: EmailSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email.ilike(request.email)).first()
    if user:
        return {
            "message": "User exists",
            "user_exists": True,
            "data": {"email": user.email, "name": user.name},
        }
    else:
        return {"message": "User does not exist", "user_exists": False}


@router.post("/register", status_code=status.HTTP_200_OK)
async def register(request: RegisterSchema, db: Session = Depends(get_db)):
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
async def verify_otp(request: VerifyOTPSchema, db: Session = Depends(get_db)):
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


@router.post("/login")
async def login(
    credentials: LoginSchema, request: Request, db: Session = Depends(get_db)
):
    user: User = authenticate_user(db, credentials.email, credentials.password)
    if not user:
        return JSONResponse(
            content={"message": "Invalid credentials"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    user_res = UserSchema.model_validate(user, from_attributes=True)

    return JSONResponse(
        content={
            "message": "Login successful",
            "data": {
                "access_token": access_token,
                "token_type": "bearer",
                "user": user_res.to_dict_with_absolute_url(request),
            },
        },
        status_code=status.HTTP_200_OK,
    )


@router.post("/forgot-password")
async def forgot_password(request: EmailSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email.ilike(request.email)).first()
    if user:
        otp = create_or_update_otp(db, user)
        # send email
        return JSONResponse(
            {"message": "OTP sent successfully", "data": {"email": user.email}},
            status_code=status.HTTP_200_OK,
        )
    else:
        return JSONResponse(
            {"message": "User does not exist"}, status_code=status.HTTP_404_NOT_FOUND
        )


@router.post("/forgot-password/verify-otp")
async def forgot_password_verify_otp(
    request: VerifyOTPSchema, db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email.ilike(request.email)).first()
    if not user:
        return JSONResponse(
            {"message": "User does not exist"}, status_code=status.HTTP_404_NOT_FOUND
        )
    db_otp = db.query(OTP).filter(OTP.email.ilike(request.email)).first()
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    if db_otp and db_otp.otp == request.otp:
        db_otp.otp = "".join([str(random.randint(0, 9)) for _ in range(10)])
        db.commit()
        db.refresh(db_otp)
        return JSONResponse(
            {
                "message": "OTP verified successfully",
                "data": {"access_token": access_token},
            },
            status_code=status.HTTP_200_OK,
        )
    else:
        return JSONResponse(
            {"message": "Invalid OTP"}, status_code=status.HTTP_400_BAD_REQUEST
        )


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if request.password != request.confirm_password:
        return JSONResponse(
            {"message": "Password and confirm password do not match"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    current_user.set_password(request.password)
    db.commit()
    db.refresh(current_user)
    return JSONResponse(
        {"message": "Password reset successfully"}, status_code=status.HTTP_200_OK
    )
