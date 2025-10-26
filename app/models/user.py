from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, JSON, Enum
from app.database import Base
import enum


class UserType(enum.Enum):
    supplier = "supplier"
    consumer = "consumer"
    admin = "admin"


class District(enum.Enum):
    Dhaka = "Dhaka"
    Chittagong = "Chittagong"
    Khulna = "Khulna"
    Rajshahi = "Rajshahi"
    Sylhet = "Sylhet"
    Rangpur = "Rangpur"
    Barisal = "Barisal"
    Mymensingh = "Mymensingh"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    picture = Column(String, nullable=True)

    user_type = Column(Enum(UserType), nullable=True)
    occupation = Column(String, nullable=True)
    district = Column(Enum(District), nullable=True, default=District.Dhaka)
    address = Column(String, nullable=True)
    tokens = Column(JSON, nullable=True)

    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, email={self.email}, phone={self.phone})"
