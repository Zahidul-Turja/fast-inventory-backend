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

    def to_dict_with_absolute_url(self, request):
        data = self.model_dump()
        if self.picture:
            # If already an absolute URL, don’t prefix again
            if not self.picture.startswith("http"):
                base_url = str(request.base_url).rstrip("/")
                data["picture"] = f"{base_url}{self.picture}"
        return data
