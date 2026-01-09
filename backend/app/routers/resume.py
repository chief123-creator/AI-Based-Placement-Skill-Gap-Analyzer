from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/status", tags=["resumes"])
async def resume_status(current_user: User = Depends(get_current_user)):
    return {
        "success": True,
        "message": "Resume endpoint is working!",
        "user_id": current_user.id
    }

@router.post("/upload", tags=["resumes"])
async def upload_resume(current_user: User = Depends(get_current_user)):
    return {
        "success": True,
        "message": "Upload endpoint is ready",
        "user_id": current_user.id
    }