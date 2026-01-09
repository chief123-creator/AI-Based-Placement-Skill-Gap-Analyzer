from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.dependencies import get_current_user

from app.services.file_handler import file_handler
from app.services.resume_parser import ResumeParser
from app.schemas.resume import ResumeUploadResponse, ResumeDetail, ResumeListItem

router = APIRouter()


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and parse resume
    
    - Accepts PDF, DOCX, DOC files
    - Max size: 10MB
    - Extracts text and skills automatically
    """
    try:
        # Step 1: Save file to disk
        file_info = await file_handler.save_uploaded_file(file, int(current_user.id))
        
        # Step 2: Parse resume
        parser = ResumeParser(db)
        parsed_data = parser.parse(str(file_info['file_path']))
        
        # Step 3: Save to database
        resume = Resume(
            user_id=current_user.id,
            original_filename=file_info['original_filename'],
            stored_filename=file_info['stored_filename'],
            file_path=file_info['file_path'],
            file_size=file_info['file_size'],
            file_type=file_info['file_type'],
            extracted_text=parsed_data['extracted_text'],
            extracted_skills=parsed_data['extracted_skills'],
            parsed_sections=parsed_data['parsed_sections']
        )
        
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        return ResumeUploadResponse(
            id=resume.id,
            original_filename=resume.original_filename,
            skills_found=parsed_data['parsed_sections']['skill_count'],
            message="Resume uploaded and parsed successfully"
        )
        
    except ValueError as e:
        # Validation or parsing errors
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Resume processing failed: {str(e)}")


@router.get("/my-resumes", response_model=List[ResumeListItem])
def get_my_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all resumes for current user"""
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).all()
    
    return [
        ResumeListItem(
            id=resume.id,
            original_filename=resume.original_filename,
            file_size=resume.file_size,
            skill_count=len(resume.extracted_skills) if resume.extracted_skills else 0,
            created_at=resume.created_at
        )
        for resume in resumes
    ]


@router.get("/{resume_id}", response_model=ResumeDetail)
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific resume details"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return resume


@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a resume"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Delete file from disk
    file_handler.delete_file(str(resume.file_path))
    
    # Delete from database
    db.delete(resume)
    db.commit()
    
    return {"message": "Resume deleted successfully"}
