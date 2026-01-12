from sqlalchemy.orm import Session
from app.models.skill import Skill
from typing import List, Dict, Tuple
import re
import logging
from app.services.skill_normalizer import get_skill_normalizer

logger = logging.getLogger(__name__)


class JDSkillExtractor:
    """Extract required skills from job descriptions with importance weighting"""
    
    # Keywords that indicate skill importance
    CRITICAL_KEYWORDS = [
        "required", "must have", "mandatory", "essential", "critical",
        "necessary", "needed", "prerequisite"
    ]
    
    PREFERRED_KEYWORDS = [
        "preferred", "nice to have", "plus", "bonus", "desirable",
        "advantageous", "beneficial"
    ]
    
    def __init__(self, db: Session):
        self.db = db
        self.skills_cache = self._load_skills()
        self.normalizer = get_skill_normalizer(db)
    
    def _load_skills(self) -> List[Skill]:
        """Load all skills from database"""
        try:
            skills = self.db.query(Skill).all()
            logger.info(f"Loaded {len(skills)} skills from database")
            return skills
        except Exception as e:
            logger.error(f"Error loading skills: {str(e)}")
            return []
    
    def extract_skills_with_importance(self, jd_text: str) -> Tuple[List[Dict], Dict[str, str]]:
        """
        Extract skills from JD text and determine their importance
        
        Args:
            jd_text: Job description text
            
        Returns:
            Tuple of:
            - List of skill dicts with {id, name, category, importance_weight}
            - Dict mapping skill names to importance level
        """
        if not jd_text:
            return [], {}
        
        # Normalize text
        normalized_text = self._normalize_text(jd_text)
        
        # Split into sections to identify context
        sections = self._split_into_sections(normalized_text)
        
        found_skills = []
        skill_importance = {}
        
        # CHANGED: First pass: extract raw skill mentions
        raw_mentions = []
        for skill in self.skills_cache:
            skill_name_lower = skill.name.lower()
            
            # Check if skill exists in text
            if skill_name_lower in normalized_text:
                raw_mentions.append(skill.name)
        
        # CHANGED: Second pass: normalize and deduplicate
        for raw_skill_name in raw_mentions:
            # Normalize the skill
            normalized_skill = self.normalizer.normalize(raw_skill_name)
            
            if normalized_skill:
                # Check if already added (avoid duplicates from synonyms)
                already_added = any(s["id"] == normalized_skill.id for s in found_skills)
                if already_added:
                    continue
                
                # Determine importance based on context
                importance = self._determine_importance(raw_skill_name.lower(), sections, normalized_text)
                weight = self._get_importance_weight(importance)
                
                found_skills.append({
                    "id": normalized_skill.id,
                    "name": normalized_skill.name,
                    "category": normalized_skill.category,
                    "importance_weight": weight
                })
                
                skill_importance[normalized_skill.name] = importance
        
        # Sort by importance weight (highest first)
        found_skills.sort(key=lambda x: x["importance_weight"], reverse=True)
        
        logger.info(f"Extracted {len(found_skills)} skills from JD")
        return found_skills, skill_importance
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for matching"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _split_into_sections(self, text: str) -> Dict[str, str]:
        """Split JD into sections (requirements, qualifications, etc.)"""
        sections = {
            "requirements": "",
            "qualifications": "",
            "responsibilities": "",
            "full_text": text
        }
        
        # Simple section detection
        req_patterns = [
            "requirements", "required skills", "must have",
            "qualifications", "required qualifications"
        ]
        
        for pattern in req_patterns:
            if pattern in text:
                # Extract text after this heading (next 500 chars as context)
                idx = text.find(pattern)
                sections["requirements"] += text[idx:idx+500] + " "
        
        return sections
    
    def _determine_importance(self, skill_name: str, sections: Dict[str, str], full_text: str) -> str:
        """Determine if skill is required, preferred, or just mentioned"""
        
        # Get context around skill mention (100 chars before and after)
        skill_contexts = []
        start = 0
        while True:
            idx = full_text.find(skill_name, start)
            if idx == -1:
                break
            context_start = max(0, idx - 100)
            context_end = min(len(full_text), idx + len(skill_name) + 100)
            skill_contexts.append(full_text[context_start:context_end])
            start = idx + 1
        
        # Check for critical keywords in context
        for context in skill_contexts:
            for keyword in self.CRITICAL_KEYWORDS:
                if keyword in context:
                    return "required"
        
        # Check for preferred keywords
        for context in skill_contexts:
            for keyword in self.PREFERRED_KEYWORDS:
                if keyword in context:
                    return "preferred"
        
        # If in requirements section, consider it required
        if skill_name in sections.get("requirements", ""):
            return "required"
        
        # Otherwise just mentioned
        return "mentioned"
    
    def _get_importance_weight(self, importance: str) -> float:
        """Convert importance level to numeric weight"""
        weights = {
            "required": 1.0,
            "preferred": 0.7,
            "mentioned": 0.5
        }
        return weights.get(importance, 0.5)


# Factory function
def get_jd_skill_extractor(db: Session) -> JDSkillExtractor:
    return JDSkillExtractor(db)