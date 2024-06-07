import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from dependencies.database import get_db
from sqlalchemy.orm import Session
from models import User
from utils.jwt_token import create_access_token
from utils.password_hash import get_password_hash, verify_password

from config import jwt_config

router = APIRouter()


class UserCredential(BaseModel):
    email: EmailStr  # EmailStr handles necessary validations for an email.
    password: str = Field(min_length=8, max_length=100)


@router.post("/signup")
def create_user(signup_cred: UserCredential, db: Session = Depends(get_db)):
    try:
        db_user = User.get_user_or_none(db, signup_cred.email)
        if db_user:
            return "User with the email already exists."

        hashed_password = get_password_hash(signup_cred.password)
        db.add(User(email=signup_cred.email, password=hashed_password))
        db.commit()
        return "User created successfully."

    except Exception as e:
        logging.debug(e)


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/login")
def login_user(login_cred: UserCredential, db: Session = Depends(get_db)):
    try:
        user = User.get_user_or_none(db, login_cred.email)

        if not user or not verify_password(login_cred.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(
            data={"email": user.email},
            secret_key=jwt_config.get("SECRET_KEY", "UNSECURE_KEY"),
            algorithm=jwt_config.get("ALGORITHM", "HS256"),
            expires_minutes=jwt_config.get("ACCESS_TOKEN_EXPIRE_MINUTES", 15),
        )

        return Token(access_token=access_token, token_type="bearer")

    except Exception as e:
        logging.debug(e)
