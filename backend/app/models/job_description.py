from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.models.user import User


class JobDescription(Base):
    __tablename__ = "job_descriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # JD Basic Information
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    
    # File information (if uploaded as file)
    original_filename = Column(String(255), nullable=True)
    stored_filename = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)  # in bytes
    file_type = Column(String(10), nullable=True)  # pdf, docx
    
    # Text content (from file or paste)
    description_text = Column(Text, nullable=False)
    
    # Parsed content
    extracted_skills = Column(JSON, nullable=True)  # List of required skills with weights
    skill_importance = Column(JSON, nullable=True)  # Skill weights/importance mapping
    
    # Embedding for similarity matching
    embedding = Column(JSON, nullable=True)  # Vector embedding as JSON array
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="job_descriptions")
