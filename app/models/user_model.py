from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, JSON, Enum, Boolean
from app.database import Base
from passlib.context import CryptContext
import enum

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
)


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
    phone = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, nullable=False)
    picture = Column(String, nullable=True)

    user_type = Column(Enum(UserType), nullable=True, default=UserType.supplier)
    occupation = Column(String, nullable=True)
    district = Column(Enum(District), nullable=True)
    address = Column(String, nullable=True)
    tokens = Column(JSON, nullable=True)
    password = Column(String, nullable=True)

    active = Column(Boolean, nullable=False, default=True)
    verified = Column(Boolean, nullable=False, default=False)
    deleted = Column(Boolean, nullable=False, default=False)

    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def set_password(self, password: str):
        self.password = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password)

    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, email={self.email}, phone={self.phone})"


class OTP(Base):
    __tablename__ = "otp"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    otp = Column(String, nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
