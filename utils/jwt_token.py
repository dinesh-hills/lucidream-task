from datetime import datetime, timedelta, timezone

import jwt


def create_access_token(
    data: dict, secret_key: str, algorithm, expires_minutes: int = 15
):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, key=secret_key, algorithm=algorithm)
    return encoded_jwt
