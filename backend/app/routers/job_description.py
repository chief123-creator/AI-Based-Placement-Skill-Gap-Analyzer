from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.job_description import JobDescription
from app.schemas.job_description import (
    JobDescriptionUploadResponse,
    JobDescriptionPasteRequest,
    JobDescriptionPasteResponse,
    JobDescriptionListItem,
    JobDescriptionDetail
)
from app.services.jd_parser import get_jd_parser
from app.services.file_handler import file_handler
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/job-descriptions", tags=["Job Descriptions"])


@router.post("/upload", response_model=JobDescriptionUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_job_description(
    file: UploadFile = File(...),
    title: str = "",
    company: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a job description file (PDF/DOCX)
    """
    try:
        # Validate file type
        allowed_extensions = [".pdf", ".docx", ".doc"]
        file_ext = file_handler.get_file_extension(file.filename)
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not supported. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save file
        file_info = await file_handler.save_file(file, folder="job_descriptions")
        
        # Parse JD from file
        jd_parser = get_jd_parser(db)
        parsed_data = jd_parser.parse_jd_from_file(file_info["file_path"])
        
        # Use title from file name if not provided
        if not title or title.strip() == "":
            title = file.filename.rsplit(".", 1)[0]
        
        # Create JD record
        jd = JobDescription(
            user_id=current_user.id,
            title=title,
            company=company if company else None,
            original_filename=file_info["original_filename"],
            stored_filename=file_info["stored_filename"],
            file_path=file_info["file_path"],
            file_size=file_info["file_size"],
            file_type=file_ext.replace(".", ""),
            description_text=parsed_data["extracted_text"],
            extracted_skills=parsed_data["extracted_skills"],
            skill_importance=parsed_data["skill_importance"],
            embedding=parsed_data["embedding"]
        )
        
        db.add(jd)
        db.commit()
        db.refresh(jd)
        
        logger.info(f"Job description uploaded successfully: ID {jd.id}")
        
        return JobDescriptionUploadResponse(
            id=jd.id,
            title=jd.title,
            company=jd.company,
            original_filename=jd.original_filename,
            skills_found=len(parsed_data["extracted_skills"]),
            message="Job description uploaded and parsed successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading job description: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload job description"
        )


@router.post("/paste", response_model=JobDescriptionPasteResponse, status_code=status.HTTP_201_CREATED)
async def paste_job_description(
    jd_data: JobDescriptionPasteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a job description by pasting text
    """
    try:
        # Parse JD from text
        jd_parser = get_jd_parser(db)
        parsed_data = jd_parser.parse_jd_from_text(jd_data.description_text)
        
        # Create JD record
        jd = JobDescription(
            user_id=current_user.id,
            title=jd_data.title,
            company=jd_data.company,
            description_text=parsed_data["extracted_text"],
            extracted_skills=parsed_data["extracted_skills"],
            skill_importance=parsed_data["skill_importance"],
            embedding=parsed_data["embedding"]
        )
        
        db.add(jd)
        db.commit()
        db.refresh(jd)
        
        logger.info(f"Job description created from text: ID {jd.id}")
        
        return JobDescriptionPasteResponse(
            id=jd.id,
            title=jd.title,
            company=jd.company,
            skills_found=len(parsed_data["extracted_skills"]),
            message="Job description created and parsed successfully"
        )
    
    except Exception as e:
        logger.error(f"Error creating job description: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create job description"
        )


@router.get("/my-jds", response_model=List[JobDescriptionListItem])
async def get_my_job_descriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all job descriptions uploaded by current user
    """
    try:
        jds = db.query(JobDescription).filter(
            JobDescription.user_id == current_user.id
        ).order_by(JobDescription.created_at.desc()).all()
        
        return [
            JobDescriptionListItem(
                id=jd.id,
                title=jd.title,
                company=jd.company,
                skills_found=len(jd.extracted_skills) if jd.extracted_skills else 0,
                created_at=jd.created_at
            )
            for jd in jds
        ]
    
    except Exception as e:
        logger.error(f"Error fetching job descriptions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch job descriptions"
        )


@router.get("/{jd_id}", response_model=JobDescriptionDetail)
async def get_job_description_detail(
    jd_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific job description
    """
    try:
        jd = db.query(JobDescription).filter(
            JobDescription.id == jd_id,
            JobDescription.user_id == current_user.id
        ).first()
        
        if not jd:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job description not found"
            )
        
        return JobDescriptionDetail(
            id=jd.id,
            title=jd.title,
            company=jd.company,
            original_filename=jd.original_filename,
            file_size=jd.file_size,
            description_text=jd.description_text,
            extracted_skills=jd.extracted_skills,
            skill_importance=jd.skill_importance,
            created_at=jd.created_at,
            updated_at=jd.updated_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching job description detail: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch job description details"
        )
