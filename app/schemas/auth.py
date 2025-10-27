from pydantic import BaseModel, EmailStr


class UserCheckRequest(BaseModel):
    email: EmailStr
