from pydantic import BaseModel, EmailStr


class UserAuth(BaseModel):
    username: str | EmailStr
    password: str