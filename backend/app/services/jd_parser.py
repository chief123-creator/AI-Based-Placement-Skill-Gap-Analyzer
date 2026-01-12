from sqlalchemy.orm import Session
from app.services.text_extractor import TextExtractor
from app.services.jd_skill_extractor import get_jd_skill_extractor
from app.services.embedding_service import embedding_service
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class JDParser:
    """Orchestrates job description parsing pipeline"""
    
    def __init__(self, db: Session):
        self.db = db
        self.text_extractor = TextExtractor()
        self.skill_extractor = get_jd_skill_extractor(db)
        self.embedding_service = embedding_service
    
    def parse_jd_from_file(self, file_path: str) -> Dict:
        """
        Parse job description from uploaded file
        
        Args:
            file_path: Path to the JD file (PDF/DOCX)
            
        Returns:
            Dict with extracted_text, skills, skill_importance, embedding
        """
        try:
            logger.info(f"Starting JD parsing from file: {file_path}")
            
            # Step 1: Extract text from file
            extracted_text = self.text_extractor.extract_text(file_path)
            if not extracted_text:
                logger.error("Failed to extract text from file")
                return self._empty_result()
            
            logger.info(f"Extracted {len(extracted_text)} characters from file")
            
            # Step 2: Extract skills with importance
            skills, skill_importance = self.skill_extractor.extract_skills_with_importance(extracted_text)
            logger.info(f"Found {len(skills)} skills in JD")
            
            # Step 3: Generate embedding
            embedding = self.embedding_service.generate_embedding(extracted_text)
            if embedding:
                logger.info(f"Generated embedding vector of length {len(embedding)}")
            else:
                logger.warning("Failed to generate embedding")
            
            return {
                "extracted_text": extracted_text,
                "extracted_skills": skills,
                "skill_importance": skill_importance,
                "embedding": embedding
            }
        
        except Exception as e:
            logger.error(f"Error parsing JD from file: {str(e)}")
            return self._empty_result()
    
    def parse_jd_from_text(self, text: str) -> Dict:
        """
        Parse job description from pasted text
        
        Args:
            text: Job description text
            
        Returns:
            Dict with extracted_text, skills, skill_importance, embedding
        """
        try:
            logger.info(f"Starting JD parsing from text ({len(text)} characters)")
            
            # Text is already provided, no extraction needed
            if not text or not text.strip():
                logger.error("Empty text provided")
                return self._empty_result()
            
            # Step 1: Extract skills with importance
            skills, skill_importance = self.skill_extractor.extract_skills_with_importance(text)
            logger.info(f"Found {len(skills)} skills in JD")
            
            # Step 2: Generate embedding
            embedding = self.embedding_service.generate_embedding(text)
            if embedding:
                logger.info(f"Generated embedding vector of length {len(embedding)}")
            else:
                logger.warning("Failed to generate embedding")
            
            return {
                "extracted_text": text,
                "extracted_skills": skills,
                "skill_importance": skill_importance,
                "embedding": embedding
            }
        
        except Exception as e:
            logger.error(f"Error parsing JD from text: {str(e)}")
            return self._empty_result()
    
    def _empty_result(self) -> Dict:
        """Return empty result structure"""
        return {
            "extracted_text": "",
            "extracted_skills": [],
            "skill_importance": {},
            "embedding": None
        }


# Factory function
def get_jd_parser(db: Session) -> JDParser:
    return JDParser(db)
