from typing import List, Dict, Set
from sqlalchemy.orm import Session
from app.models.skill import Skill
import re
from app.services.skill_normalizer import get_skill_normalizer


class SkillExtractor:
    """Extract skills from resume text using database skills"""
    
    def __init__(self, db: Session):
        self.db = db
        self.skills_cache = self._load_skills()  # CHANGED: Now returns the cache
        self.normalizer = get_skill_normalizer(db)  # ADDED: Initialize normalizer
    
    def _load_skills(self) -> Dict[int, Dict]:
        """Load all skills from database into memory for fast matching"""
        skills = self.db.query(Skill).all()
        cache = {}  # CHANGED: Create local cache to return
        
        for skill in skills:
            cache[skill.id] = {
                'name': skill.name.lower(),
                'category': skill.category,
                'aliases': []
            }
        
        return cache  # CHANGED: Return the cache
    
    def extract_skills(self, text: str) -> List[int]:
        """
        Extract skill IDs from text
        
        Args:
            text: Resume text
            
        Returns:
            List of matched skill IDs
        """
        if not text:
            return []
        
        text_lower = text.lower()
        matched_skill_ids = set()
        
        # Check each skill in cache
        for skill_id, skill_data in self.skills_cache.items():
            skill_name = skill_data['name']
            
            # Exact word boundary match
            if self._find_skill_in_text(skill_name, text_lower):
                matched_skill_ids.add(skill_id)
        
        return list(matched_skill_ids)
    
    def _find_skill_in_text(self, skill: str, text: str) -> bool:
        """
        Check if skill exists in text as a whole word
        
        Args:
            skill: Skill name (lowercase)
            text: Text to search (lowercase)
            
        Returns:
            True if skill found
        """
        # Create word boundary pattern
        # \b ensures we match whole words only
        pattern = r'\b' + re.escape(skill) + r'\b'
        return bool(re.search(pattern, text))
    
    def get_skill_names(self, skill_ids: List[int]) -> List[str]:
        """Convert skill IDs back to readable names"""
        return [
            self.skills_cache[sid]['name'].title()
            for sid in skill_ids
            if sid in self.skills_cache
        ]
    
    def get_skills_by_category(self, skill_ids: List[int]) -> Dict[str, List[str]]:
        """Group extracted skills by category"""
        categorized = {}
        
        for skill_id in skill_ids:
            if skill_id in self.skills_cache:
                skill_data = self.skills_cache[skill_id]
                category = skill_data['category'] or 'Other'
                skill_name = skill_data['name'].title()
                
                if category not in categorized:
                    categorized[category] = []
                categorized[category].append(skill_name)
        
        return categorized
    
    # ADDED: New method to extract and normalize skills
    def extract_and_normalize_skills(self, text: str) -> List[Dict]:
        """
        Extract skills from text and normalize them
        
        Returns:
            List of dicts with normalized skill info
        """
        # First, extract raw skill IDs using existing logic
        raw_skill_ids = self.extract_skills(text)
        
        # Then normalize them
        normalized_skills = []
        seen_ids = set()
        
        for skill_id in raw_skill_ids:
            if skill_id in self.skills_cache:
                skill_data = self.skills_cache[skill_id]
                # Normalize the skill name using the normalizer
                normalized = self.normalizer.normalize(skill_data['name'])
                
                if normalized and normalized.id not in seen_ids:
                    normalized_skills.append({
                        "id": normalized.id,
                        "name": normalized.name,
                        "category": normalized.category
                    })
                    seen_ids.add(normalized.id)
        
        return normalized_skills