from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str]


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: str


class UserInDB(UserBase):
    id: str
    password_hash: str
