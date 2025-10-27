from pydantic import BaseModel, EmailStr


class UserCheckRequest(BaseModel):
    email: EmailStr


class UserRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    confirm_password: str


class UserVerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str


class UserDetailsResponse(BaseModel):
    name: str
    email: EmailStr
    phone: str | None
    picture: str | None
    user_type: str | None
    occupation: str | None
    district: str | None
    address: str | None
    verified: bool

    class Config:
        orm_mode = True
