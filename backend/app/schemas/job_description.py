from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


# Request schemas
class JobDescriptionUploadResponse(BaseModel):
    id: int
    title: str
    company: Optional[str]
    original_filename: Optional[str]
    skills_found: int
    message: str

    class Config:
        from_attributes = True


class JobDescriptionPasteRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    description_text: str = Field(..., min_length=10)


class JobDescriptionPasteResponse(BaseModel):
    id: int
    title: str
    company: Optional[str]
    skills_found: int
    message: str

    class Config:
        from_attributes = True


# Response schemas
class JobDescriptionListItem(BaseModel):
    id: int
    title: str
    company: Optional[str]
    skills_found: int
    created_at: datetime

    class Config:
        from_attributes = True


class JobDescriptionDetail(BaseModel):
    id: int
    title: str
    company: Optional[str]
    original_filename: Optional[str]
    file_size: Optional[int]
    description_text: str
    extracted_skills: Optional[List[Dict]]
    skill_importance: Optional[Dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
