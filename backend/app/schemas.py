# backend/app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    nom: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    nom: str
    email: EmailStr
    photo_profil: Optional[str] = None

    class Config:
        from_attributes = True

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"