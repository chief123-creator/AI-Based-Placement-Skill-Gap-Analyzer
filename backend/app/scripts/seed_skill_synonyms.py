"""
Script to populate common skill synonyms
Run with: python -m app.scripts.seed_skill_synonyms
"""

from app.database import SessionLocal
from app.models.skill import Skill
from app.models.skill_synonym import SkillSynonym
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Common skill synonym mappings
SYNONYM_MAPPINGS = {
    "JavaScript": ["JS", "js", "Javascript", "javascript", "ECMAScript"],
    "TypeScript": ["TS", "ts", "Typescript", "typescript"],
    "Python": ["python", "py"],
    "React": ["ReactJS", "React.js", "Reactjs"],
    "Node.js": ["NodeJS", "Node", "nodejs", "node"],
    "MongoDB": ["Mongo", "mongo", "mongodb"],
    "PostgreSQL": ["Postgres", "postgres", "postgresql", "psql"],
    "MySQL": ["mysql", "My SQL"],
    "Docker": ["docker", "Dockerfile"],
    "Kubernetes": ["K8s", "k8s", "kubernetes", "kube"],
    "Amazon Web Services": ["AWS", "aws"],
    "Machine Learning": ["ML", "ml"],
    "Artificial Intelligence": ["AI", "ai"],
    "Natural Language Processing": ["NLP", "nlp"],
    "Deep Learning": ["DL", "dl"],
    "REST API": ["REST", "RESTful", "rest api", "restful api"],
    "GraphQL": ["graphql", "Graph QL"],
    "HTML": ["HTML5", "html", "html5"],
    "CSS": ["CSS3", "css", "css3"],
    "SQL": ["sql", "Structured Query Language"],
    "NoSQL": ["nosql", "No SQL"],
    "Git": ["git", "Github", "GitHub"],
    "FastAPI": ["fastapi", "Fast API"],
    "Flask": ["flask"],
    "Django": ["django"],
    "Express": ["ExpressJS", "Express.js", "expressjs"],
    "Vue": ["VueJS", "Vue.js", "Vuejs"],
    "Angular": ["AngularJS", "Angular.js"],
    "TailwindCSS": ["Tailwind", "tailwind", "tailwindcss"],
    "Bootstrap": ["bootstrap"],
    "Redis": ["redis"],
    "Elasticsearch": ["elasticsearch", "Elastic Search", "ES"],
    "Jenkins": ["jenkins"],
    "CI/CD": ["CICD", "Continuous Integration", "Continuous Deployment"],
}


def seed_synonyms():
    """Populate skill synonyms in database"""
    db = SessionLocal()
    
    try:
        added_count = 0
        skipped_count = 0
        
        for canonical_name, synonyms in SYNONYM_MAPPINGS.items():
            # Find the canonical skill
            skill = db.query(Skill).filter(Skill.name.ilike(canonical_name)).first()
            
            if not skill:
                logger.warning(f"Skill '{canonical_name}' not found in database, skipping...")
                skipped_count += len(synonyms)
                continue
            
            # Add each synonym
            for synonym in synonyms:
                # Check if synonym already exists
                existing = db.query(SkillSynonym).filter(
                    SkillSynonym.synonym == synonym
                ).first()
                
                if existing:
                    logger.info(f"Synonym '{synonym}' already exists, skipping...")
                    skipped_count += 1
                    continue
                
                # Create new synonym
                new_synonym = SkillSynonym(
                    synonym=synonym,
                    canonical_skill_id=skill.id
                )
                
                db.add(new_synonym)
                added_count += 1
                logger.info(f"Added: '{synonym}' -> '{canonical_name}'")
        
        # Commit all changes
        db.commit()
        
        logger.info(f"\n✅ Synonym seeding complete!")
        logger.info(f"   Added: {added_count}")
        logger.info(f"   Skipped: {skipped_count}")
    
    except Exception as e:
        logger.error(f"Error seeding synonyms: {str(e)}")
        db.rollback()
    
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Starting skill synonym seeding...")
    seed_synonyms()
