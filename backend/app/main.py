from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging import setup_logging
from app.middleware import CustomExceptionHandlerMiddleware
from app.routers import health, auth  # ← ADD auth here
from app.core.config import settings
from app.database import engine, Base

setup_logging()
app = FastAPI(title="AI Placement Analyzer", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(CustomExceptionHandlerMiddleware)

app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")  # ← ADD this line

@app.get("/")
def root():
    return {"message": "AI Placement & Skill Gap Analyzer API"}
Base.metadata.create_all(bind=engine)