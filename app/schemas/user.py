from pydantic import BaseModel

from app.models.user import User


class UserSchema(BaseModel):
    id: int
    email: str
    phone: str
    name: str
    picture: str
    user_type: str
    occupation: str
    district: str
    address: str
    created_at: str
