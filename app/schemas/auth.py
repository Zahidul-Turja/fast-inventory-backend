from pydantic import BaseModel, EmailStr


class EmailSchema(BaseModel):
    email: EmailStr


class RegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str
    confirm_password: str


class VerifyOTPSchema(BaseModel):
    email: EmailStr
    otp: str


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class ResetPasswordSchema(BaseModel):
    password: str
    confirm_password: str


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
        # orm_mode = True
        from_attributes = True
