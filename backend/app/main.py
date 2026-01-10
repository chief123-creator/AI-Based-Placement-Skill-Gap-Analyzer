from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Direct imports - NO from app.routers import ...
from app.routers.health import router as health_router
from app.routers.auth import router as auth_router
from app.routers.resume import router as resume_router
from app.routers import job_description
from app.database import engine, Base

app = FastAPI(title="AI Placement API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with CORRECT prefixes
app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(resume_router, prefix="/api/v1/resumes")  # NOTE: Different prefix!
app.include_router(job_description.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/api")
def api_info():
    return {
        "endpoints": {
            "health": "/api/v1/health",
            "auth": "/api/v1/auth",
            "resumes": "/api/v1/resumes"
        }
    }

Base.metadata.create_all(bind=engine)