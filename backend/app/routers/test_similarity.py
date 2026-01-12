from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.services.similarity_calculator import similarity_calculator

router = APIRouter(prefix="/test", tags=["Testing"])


@router.get("/similarity/{resume_id}/{jd_id}")
async def test_similarity(
    resume_id: int,
    jd_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Test similarity calculation between a resume and JD"""
    
    # Get resume
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Get JD
    jd = db.query(JobDescription).filter(
        JobDescription.id == jd_id,
        JobDescription.user_id == current_user.id
    ).first()
    
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    # Calculate similarity
    result = similarity_calculator.calculate_resume_jd_similarity(
        resume.embedding,
        jd.embedding
    )
    
    return {
        "resume_id": resume_id,
        "jd_id": jd_id,
        "resume_title": resume.original_filename,
        "jd_title": jd.title,
        "similarity_score": result["similarity_score"],
        "similarity_percentage": result["similarity_percentage"],
        "has_resume_embedding": resume.embedding is not None,
        "has_jd_embedding": jd.embedding is not None
    }
