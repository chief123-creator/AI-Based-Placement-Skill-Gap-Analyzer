from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.user import UserCreate, UserOut, Token
from app.dependencies import get_admin_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email exists")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=user.role
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Could not create user")
    
    # Return WITHOUT is_active (use model_validate to avoid typing Column[...] issues)
    return UserOut.model_validate(db_user)
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, str(user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token with user ID as subject
    access_token = create_access_token(
        data={
            "sub": str(user.id),  # User ID as string
            "email": user.email
        }
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/check-email")
def check_email(email: str, db: Session = Depends(get_db)):
    """Check whether the provided email exists in the user table."""
    exists = db.query(User).filter(User.email == email).first() is not None
    return {"email": email, "exists": exists}

from app.dependencies import get_admin_user

@router.get("/check-admin")
def check_admin(current_user: User = Depends(get_admin_user)):
    """Admin-only endpoint to verify role-based access."""
    return {"admin": current_user.email, "role": current_user.role}
