from fastapi import APIRouter, Depends
from app.schemas.user import UserOut
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/protected", tags=["protected"])

@router.get("/profile", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user
