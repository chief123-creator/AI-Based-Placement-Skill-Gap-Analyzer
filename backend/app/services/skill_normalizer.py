from sqlalchemy.orm import Session
from app.models.skill import Skill
from app.models.skill_synonym import SkillSynonym
from typing import Optional, Dict, List
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)


class SkillNormalizer:
    """Normalize skill names using synonyms and fuzzy matching"""
    
    def __init__(self, db: Session):
        self.db = db
        self.skill_map = {}  # canonical_name -> Skill object
        self.synonym_map = {}  # synonym -> canonical Skill object
        self._load_skills()
    
    def _load_skills(self):
        """Load all skills and synonyms into memory for fast lookup"""
        try:
            # Load all skills
            skills = self.db.query(Skill).all()
            for skill in skills:
                self.skill_map[skill.name.lower()] = skill
            
            # Load all synonyms
            synonyms = self.db.query(SkillSynonym).all()
            for syn in synonyms:
                self.synonym_map[syn.synonym.lower()] = syn.canonical_skill
            
            logger.info(f"Loaded {len(self.skill_map)} skills and {len(self.synonym_map)} synonyms")
        
        except Exception as e:
            logger.error(f"Error loading skills: {str(e)}")
    
    def normalize(self, skill_text: str) -> Optional[Skill]:
        """
        Normalize a skill name to its canonical form
        
        Args:
            skill_text: Raw skill name (e.g., "JS", "react.js", "Reactjs")
            
        Returns:
            Canonical Skill object or None if no match found
        """
        if not skill_text or not skill_text.strip():
            return None
        
        # Clean input
        cleaned = self._clean_skill_name(skill_text)
        
        # Step 1: Exact match in canonical skills
        if cleaned in self.skill_map:
            return self.skill_map[cleaned]
        
        # Step 2: Exact match in synonyms
        if cleaned in self.synonym_map:
            return self.synonym_map[cleaned]
        
        # Step 3: Fuzzy match
        fuzzy_match = self._fuzzy_match(cleaned)
        if fuzzy_match:
            return fuzzy_match
        
        # No match found
        return None
    
    def normalize_list(self, skill_texts: List[str]) -> List[Skill]:
        """
        Normalize a list of skill names
        
        Args:
            skill_texts: List of raw skill names
            
        Returns:
            List of unique canonical Skill objects
        """
        normalized_skills = []
        seen_ids = set()
        
        for skill_text in skill_texts:
            skill = self.normalize(skill_text)
            if skill and skill.id not in seen_ids:
                normalized_skills.append(skill)
                seen_ids.add(skill.id)
        
        return normalized_skills
    
    def _clean_skill_name(self, skill_text: str) -> str:
        """Clean and standardize skill name"""
        # Convert to lowercase
        cleaned = skill_text.lower().strip()
        
        # Remove common variations
        cleaned = cleaned.replace(".", "")  # react.js -> reactjs
        cleaned = cleaned.replace("-", "")  # node-js -> nodejs
        cleaned = cleaned.replace("_", "")  # node_js -> nodejs
        cleaned = cleaned.replace(" ", "")  # node js -> nodejs
        
        return cleaned
    
    def _fuzzy_match(self, skill_text: str, threshold: float = 0.85) -> Optional[Skill]:
        """
        Find best fuzzy match for a skill name
        
        Args:
            skill_text: Cleaned skill name
            threshold: Similarity threshold (0-1), default 0.85
            
        Returns:
            Best matching Skill object or None
        """
        best_match = None
        best_score = 0.0
        
        # Check against canonical skills
        for canonical_name, skill in self.skill_map.items():
            score = SequenceMatcher(None, skill_text, canonical_name).ratio()
            if score > best_score and score >= threshold:
                best_score = score
                best_match = skill
        
        # Check against synonyms
        for synonym, skill in self.synonym_map.items():
            score = SequenceMatcher(None, skill_text, synonym).ratio()
            if score > best_score and score >= threshold:
                best_score = score
                best_match = skill
        
        if best_match:
            logger.info(f"Fuzzy matched '{skill_text}' to '{best_match.name}' (score: {best_score:.2f})")
        
        return best_match
    
    def add_synonym(self, synonym: str, canonical_skill_name: str) -> bool:
        """
        Add a new synonym mapping
        
        Args:
            synonym: The synonym to add (e.g., "JS")
            canonical_skill_name: The canonical skill name (e.g., "JavaScript")
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            # Find canonical skill
            canonical_skill = self.db.query(Skill).filter(
                Skill.name.ilike(canonical_skill_name)
            ).first()
            
            if not canonical_skill:
                logger.warning(f"Canonical skill '{canonical_skill_name}' not found")
                return False
            
            # Check if synonym already exists
            existing = self.db.query(SkillSynonym).filter(
                SkillSynonym.synonym.ilike(synonym)
            ).first()
            
            if existing:
                logger.warning(f"Synonym '{synonym}' already exists")
                return False
            
            # Create new synonym
            new_synonym = SkillSynonym(
                synonym=synonym,
                canonical_skill_id=canonical_skill.id
            )
            
            self.db.add(new_synonym)
            self.db.commit()
            
            # Update in-memory cache
            self.synonym_map[synonym.lower()] = canonical_skill
            
            logger.info(f"Added synonym '{synonym}' -> '{canonical_skill.name}'")
            return True
        
        except Exception as e:
            logger.error(f"Error adding synonym: {str(e)}")
            self.db.rollback()
            return False
    
    def get_canonical_name(self, skill_text: str) -> Optional[str]:
        """
        Get the canonical name for a skill
        
        Args:
            skill_text: Raw skill name
            
        Returns:
            Canonical skill name or None
        """
        skill = self.normalize(skill_text)
        return str(skill.name) if skill and skill.name is not None else None


# Factory function
def get_skill_normalizer(db: Session) -> SkillNormalizer:
    return SkillNormalizer(db)
