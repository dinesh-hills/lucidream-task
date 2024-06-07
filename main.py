from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, constr, field_validator

app = FastAPI()


class EmailSignUpModel(BaseModel):
    email: EmailStr  # EmailStr handles necessary validations for an email.
    password: str = constr(min_length=8, max_length=80)


@app.get("/signup")
def signup_user(user: EmailSignUpModel):
    print(user)
    return user
