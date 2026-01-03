from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    STUDENT = "student"
    ADMIN = "admin"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.STUDENT

class UserCreate(UserBase):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Keep all existing code, ADD this at bottom:
class UserOut(UserBase):
    id: int
    
    class Config:
        from_attributes = True

# Add this helper (Pydantic v2 fix)
def user_to_orm(user):
    return UserOut(id=user.id, email=user.email, full_name=user.full_name, role=user.role)
