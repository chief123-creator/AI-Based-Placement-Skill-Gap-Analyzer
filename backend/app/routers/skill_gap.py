from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.services.skill_gap_analyzer import get_skill_gap_analyzer
from typing import Dict
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/skill-gap", tags=["Skill Gap Analysis"])


@router.get("/analyze/{resume_id}/{jd_id}", response_model=Dict)
async def analyze_skill_gap(
    resume_id: int,
    jd_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze skill gap between a resume and job description
    
    Returns:
    - Match score (0-100)
    - Matched skills
    - Missing skills (with priority)
    - Weak/irrelevant skills
    - Detailed score breakdown
    - Explainable recommendations
    """
    try:
        # Get resume
        resume = db.query(Resume).filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        ).first()
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        # Get job description
        jd = db.query(JobDescription).filter(
            JobDescription.id == jd_id,
            JobDescription.user_id == current_user.id
        ).first()
        
        if not jd:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job description not found"
            )
        
        # Validate data
        if resume.extracted_skills is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume has no extracted skills. Please re-upload the resume."
            )
        
        if jd.extracted_skills is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job description has no extracted skills. Please re-upload the JD."
            )
        
        # Perform analysis
        analyzer = get_skill_gap_analyzer(db)
        analysis = analyzer.analyze(resume, jd)
        
        # Add metadata
        analysis["resume_id"] = resume_id
        analysis["jd_id"] = jd_id
        analysis["resume_filename"] = resume.original_filename
        analysis["jd_title"] = jd.title
        analysis["jd_company"] = jd.company
        
        logger.info(f"Skill gap analysis completed: Resume {resume_id} vs JD {jd_id} - Score: {analysis['match_score']}")
        
        return analysis
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing skill gap: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze skill gap"
        )


@router.get("/compare-resume/{resume_id}", response_model=Dict)
async def compare_resume_with_all_jds(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compare a resume against all user's job descriptions
    
    Returns ranked list of JDs by match score
    """
    try:
        # Get resume
        resume = db.query(Resume).filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        ).first()
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        # Get all user's JDs
        jds = db.query(JobDescription).filter(
            JobDescription.user_id == current_user.id
        ).all()
        
        if not jds:
            return {
                "resume_id": resume_id,
                "resume_filename": resume.original_filename,
                "matches": [],
                "message": "No job descriptions found to compare"
            }
        
        # Analyze against each JD
        analyzer = get_skill_gap_analyzer(db)
        matches = []
        
        for jd in jds:
            if jd.extracted_skills is None:
                continue
            
            analysis = analyzer.analyze(resume, jd)
            
            matches.append({
                "jd_id": jd.id,
                "jd_title": jd.title,
                "jd_company": jd.company,
                "match_score": analysis["match_score"],
                "match_level": analysis["explanation"]["match_level"],
                "matched_skills_count": len(analysis["matched_skills"]),
                "missing_skills_count": len(analysis["missing_skills"]),
                "recommendation": analysis["explanation"]["recommendation"]
            })
        
        # Sort by match score (highest first)
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {
            "resume_id": resume_id,
            "resume_filename": resume.original_filename,
            "total_jds_compared": len(matches),
            "matches": matches
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing resume with JDs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compare resume with job descriptions"
        )
