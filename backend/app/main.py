from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging import setup_logging
from app.middleware import CustomExceptionHandlerMiddleware
from app.routers import health
from app.core.config import settings

setup_logging()
app = FastAPI(title="AI Placement Analyzer", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(CustomExceptionHandlerMiddleware)
app.include_router(health.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "AI Placement & Skill Gap Analyzer API"}
