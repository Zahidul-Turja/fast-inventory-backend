import traceback
import os
from uuid import uuid4

from fastapi import APIRouter, Depends, status, Form, File, UploadFile, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.utilities.auth import get_current_user
from app.models.user_model import User
from app.schemas.user_schema import UserSchema

PROFILE_PIC_DIR = "app/static/profile_pics"

router = APIRouter()


@router.get("/me")
async def profile(request: Request, user: User = Depends(get_current_user)):
    if not user:
        return JSONResponse(
            {"message": "User not found"}, status_code=status.HTTP_404_NOT_FOUND
        )
    user_res = UserSchema.model_validate(user, from_attributes=True)
    return {
        "message": "User profile data",
        "data": user_res.to_dict_with_absolute_url(request),
    }


@router.put("/me")
async def update_profile(
    request: Request,
    name: str = Form(None),
    phone: str = Form(None),
    district: str = Form(None),
    address: str = Form(None),
    occupation: str = Form(None),
    picture: UploadFile = File(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user:
        return JSONResponse(
            {"message": "User not found"}, status_code=status.HTTP_404_NOT_FOUND
        )

    # ✅ Handle image upload
    if picture:
        ext = picture.filename.split(".")[-1]
        filename = f"{uuid4()}.{ext}"
        filepath = os.path.join(PROFILE_PIC_DIR, filename)

        # Save file to disk
        with open(filepath, "wb") as buffer:
            buffer.write(await picture.read())

        # Update picture field
        user.picture = f"/static/profile_pics/{filename}"

    # ✅ Update other fields dynamically
    if name:
        user.name = name
    if phone:
        user.phone = phone
    if district:
        user.district = district
    if address:
        user.address = address
    if occupation:
        user.occupation = occupation

    db.commit()
    db.refresh(user)

    user_res = UserSchema.model_validate(user, from_attributes=True)
    return {
        "message": "Profile updated successfully",
        "data": user_res.to_dict_with_absolute_url(request),
    }
