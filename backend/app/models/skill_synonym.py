from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class SkillSynonym(Base):
    __tablename__ = "skill_synonyms"
    
    id = Column(Integer, primary_key=True, index=True)
    synonym = Column(String, unique=True, nullable=False, index=True)  # e.g., "JS", "React.js"
    canonical_skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Add foreign key to users table
    
    # Relationship to the canonical skill
    canonical_skill = relationship("Skill", backref="synonyms")
    user = relationship("User", back_populates="synonyms")  # Add relationship to User
