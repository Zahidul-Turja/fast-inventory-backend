from pydantic import BaseModel, EmailStr


class UserCheckRequest(BaseModel):
    email: EmailStr


class UserRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    confirm_password: str
