import random
from sqlalchemy.orm import Session
from app.models.user import User, OTP
from typing import Dict


def create_user(db: Session, user: Dict) -> User:
    print("user", user)
    db_user = User(
        name=user["name"],
        email=user["email"],
    )
    db_user.set_password(password=user["password"])
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_or_update_otp(db: Session, user: User) -> OTP:
    db_otp = db.query(OTP).filter(OTP.email == user.email).first()
    # otp = "".join([str(random.randint(0, 9)) for _ in range(4)])
    otp = "1234"
    if db_otp:
        db_otp.otp = otp
        db.commit()
        db.refresh(db_otp)
    else:
        db_otp = OTP(email=user.email, otp=otp)
        db.add(db_otp)
        db.commit()
        db.refresh(db_otp)

    return db_otp


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not user.verify_password(password):
        return None
    return user
