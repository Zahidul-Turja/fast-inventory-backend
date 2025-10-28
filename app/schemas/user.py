from pydantic import BaseModel, EmailStr

from app.models.user import User


class UserSchema(BaseModel):
    # id: int
    name: str
    email: EmailStr
    phone: str | None
    picture: str | None
    user_type: str
    occupation: str | None
    district: str | None
    address: str | None
    verified: bool

    class Config:
        # orm_mode = True
        from_attributes = True
