from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime


class ResumeUploadResponse(BaseModel):
    """Response after uploading resume"""
    id: int
    original_filename: str
    skills_found: int
    message: str
    
    class Config:
        from_attributes = True


class ResumeDetail(BaseModel):
    """Detailed resume information"""
    id: int
    original_filename: str
    stored_filename: str
    file_size: int
    file_type: str
    extracted_skills: Optional[List[int]] = None
    parsed_sections: Optional[Dict] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ResumeListItem(BaseModel):
    """Resume item for list view"""
    id: int
    original_filename: str
    file_size: int
    skill_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True
