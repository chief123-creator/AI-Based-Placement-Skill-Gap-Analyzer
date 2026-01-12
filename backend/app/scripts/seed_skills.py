"""Seed initial skills into the database."""
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.skill import Skill

# Create tables
Base.metadata.create_all(bind=engine)

def seed_skills():
    """Populate initial skills."""
    db = SessionLocal()
    
    # Check if skills already exist
    existing = db.query(Skill).first()
    if existing:
        print("Skills already seeded!")
        return
    
    skills_data = [
        # Frontend Skills
        ("Python", "backend", "High-level programming language for backend development"),
        ("JavaScript", "frontend", "Core language for web development"),
        ("React", "frontend", "JavaScript library for building user interfaces"),
        ("Vue.js", "frontend", "Progressive JavaScript framework"),
        ("TypeScript", "frontend", "Typed superset of JavaScript"),
        ("HTML/CSS", "frontend", "Markup and styling for web"),
        ("Tailwind CSS", "frontend", "Utility-first CSS framework"),
        
        # Backend Skills
        ("FastAPI", "backend", "Modern Python web framework"),
        ("Django", "backend", "Full-featured Python web framework"),
        ("Node.js", "backend", "JavaScript runtime for backend"),
        ("Express.js", "backend", "Minimalist Node.js framework"),
        ("SQL", "backend", "Database query language"),
        ("PostgreSQL", "backend", "Relational database system"),
        ("MongoDB", "backend", "NoSQL document database"),
        ("REST APIs", "backend", "Architectural pattern for web services"),
        
        # ML/AI Skills
        ("Machine Learning", "ml", "Algorithms and models for predictions"),
        ("TensorFlow", "ml", "Deep learning framework by Google"),
        ("PyTorch", "ml", "Deep learning framework by Meta"),
        ("Scikit-learn", "ml", "Machine learning library for Python"),
        ("Pandas", "ml", "Data manipulation and analysis"),
        ("NumPy", "ml", "Numerical computing library"),
        ("Data Analysis", "ml", "Statistical analysis and visualization"),
        ("Natural Language Processing", "ml", "Processing and understanding text"),
        ("Computer Vision", "ml", "Image processing and recognition"),
    ]
    
    for name, category, description in skills_data:
        skill = Skill(name=name, category=category, description=description)
        db.add(skill)
    
    db.commit()
    print(f"✅ Successfully seeded {len(skills_data)} skills!")
    db.close()

if __name__ == "__main__":
    seed_skills()
