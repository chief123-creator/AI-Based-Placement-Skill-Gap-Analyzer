from typing import Dict, List
from sqlalchemy.orm import Session
from app.services.text_extractor import TextExtractor
from app.services.skill_extractor import SkillExtractor
from app.services.embedding_service import embedding_service


class ResumeParser:
    """Main parser that orchestrates text extraction and skill extraction"""
    
    def __init__(self, db: Session):
        self.db = db
        self.text_extractor = TextExtractor()
        self.skill_extractor = SkillExtractor(db)
        self.embedding_service = embedding_service
    
    def parse(self, file_path: str) -> Dict:
        """
        Parse resume and extract all information
        
        Args:
            file_path: Path to resume file
            
        Returns:
            Dictionary with extracted data:
            {
                'extracted_text': str,
                'extracted_skills': [skill_ids],
                'parsed_sections': {
                    'skills': [skill_names],
                    'skill_count': int,
                    'skills_by_category': {...}
                }
            }
        """
        # Step 1: Extract text
        extracted_text = self.text_extractor.extract(file_path)
        
        # Validate text
        if not extracted_text or len(extracted_text) < 50:
            raise ValueError("Resume text is too short or empty. Please upload a valid resume.")
        
        # Step 2: Extract skills
        skill_ids = self.skill_extractor.extract_skills(extracted_text)
        skill_names = self.skill_extractor.get_skill_names(skill_ids)
        skills_by_category = self.skill_extractor.get_skills_by_category(skill_ids)
        
        #Step 3: Generate embedding
        embedding = self.embedding_service.generate_embedding(extracted_text)

        # Step 4: Build response
        return {
            'extracted_text': extracted_text,
            'extracted_skills': skill_ids,
            'parsed_sections': {
                'skills': skill_names,
                'skill_count': len(skill_ids),
                'skills_by_category': skills_by_category
            },
            'embedding': embedding  # MOVED HERE
        }

