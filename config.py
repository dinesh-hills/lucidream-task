DATABASE_URL = "sqlite:///dev.db"


jwt_config = dict(
    # JWT Auth Configuration
    SECRET_KEY="UNSECURE_JWT_SECRETKEY",
    ALGORITHM="HS256",
    ACCESS_TOKEN_EXPIRE_MINUTES=30,
)
