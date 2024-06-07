from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from dependencies.database import get_db
from sqlalchemy.orm import Session

import jwt
from jwt.exceptions import InvalidTokenError


from config import jwt_config
from models import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class TokenData(BaseModel):
    email: str | None = None


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, jwt_config.get("SECRET_KEY"), jwt_config.get("ALGORITHM")
        )
        user_email: str = payload.get("email")
        if user_email is None:
            raise credentials_exception
        token_data = TokenData(email=user_email)
    except InvalidTokenError:
        raise credentials_exception

    user = User.get_user_or_none(db, email=token_data.email)

    if user is None:
        raise credentials_exception

    return user
