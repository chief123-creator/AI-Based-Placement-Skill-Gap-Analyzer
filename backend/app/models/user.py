from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class UserRole(str, Enum):
    STUDENT = "student"
    ADMIN = "admin"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.STUDENT

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class TokenData(BaseModel):
    email: Optional[str] = None


# SQLAlchemy ORM model for database operations
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default=UserRole.STUDENT.value)
    is_active = Column(Boolean, nullable=False, default=True)
    resumes = relationship("Resume", back_populates="user")
    job_descriptions = relationship("JobDescription", back_populates="user")
