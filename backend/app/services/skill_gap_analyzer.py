from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.services.similarity_calculator import similarity_calculator
import logging

logger = logging.getLogger(__name__)


class SkillGapAnalyzer:
    """Analyze skill gaps between resume and job description"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def analyze(self, resume: Resume, jd: JobDescription) -> Dict:
        """
        Complete skill gap analysis between resume and JD
        
        Args:
            resume: Resume object with skills and embedding
            jd: JobDescription object with skills and embedding
            
        Returns:
            Comprehensive analysis dict with match score and explanations
        """
        try:
            # Extract skills from resume and JD
            resume_skills = self._get_skills_dict(list(resume.extracted_skills) if isinstance(resume.extracted_skills, list) else [])
            jd_skills = self._get_skills_dict(list(jd.extracted_skills) if isinstance(jd.extracted_skills, list) else [])
            jd_skill_importance = dict(jd.skill_importance) if isinstance(jd.skill_importance, dict) else {}
            
            # Identify matched, missing, and weak skills
            matched_skills = self._identify_matched_skills(resume_skills, jd_skills, jd_skill_importance)
            missing_skills = self._identify_missing_skills(resume_skills, jd_skills, jd_skill_importance)
            weak_skills = self._identify_weak_skills(resume_skills, jd_skills)
            
            # Calculate overall similarity
            similarity = similarity_calculator.calculate_resume_jd_similarity(
                resume.embedding if isinstance(resume.embedding, list) else None,
                list(jd.embedding) if isinstance(jd.embedding, list) else None
            )
            
            # Calculate match score with detailed breakdown
            match_score_breakdown = self._calculate_match_score(
                matched_skills,
                missing_skills,
                jd_skills,
                jd_skill_importance,
                similarity["similarity_score"]
            )
            
            # Generate explanation
            explanation = self._generate_explanation(
                match_score_breakdown,
                matched_skills,
                missing_skills,
                len(resume_skills),
                len(jd_skills)
            )
            
            return {
                "match_score": match_score_breakdown["total_score"],
                "match_percentage": round(match_score_breakdown["total_score"], 2),
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "weak_skills": weak_skills,
                "score_breakdown": match_score_breakdown,
                "explanation": explanation,
                "overall_similarity": similarity["similarity_percentage"],
                "resume_skill_count": len(resume_skills),
                "jd_skill_count": len(jd_skills)
            }
        
        except Exception as e:
            logger.error(f"Error analyzing skill gap: {str(e)}")
            return self._empty_result()
    
    def _get_skills_dict(self, skills_list: List[Dict]) -> Dict[int, Dict]:
        """Convert skills list to dict with skill_id as key"""
        return {
            skill["id"]: skill
            for skill in skills_list
            if isinstance(skill, dict) and "id" in skill
        }
    
    def _identify_matched_skills(self, resume_skills: Dict, jd_skills: Dict, 
                                 jd_importance: Dict) -> List[Dict]:
        """Identify skills present in both resume and JD"""
        matched = []
        
        for skill_id, skill_info in jd_skills.items():
            if skill_id in resume_skills:
                skill_name = skill_info.get("name", "Unknown")
                importance = jd_importance.get(skill_name, "mentioned")
                importance_weight = jd_skills[skill_id].get("importance_weight", 0.5)
                
                matched.append({
                    "id": skill_id,
                    "name": skill_name,
                    "category": skill_info.get("category", "Unknown"),
                    "importance": importance,
                    "importance_weight": importance_weight
                })
        
        # Sort by importance weight (highest first)
        matched.sort(key=lambda x: x["importance_weight"], reverse=True)
        
        return matched
    
    def _identify_missing_skills(self, resume_skills: Dict, jd_skills: Dict,
                                 jd_importance: Dict) -> List[Dict]:
        """Identify skills required in JD but missing in resume"""
        missing = []
        
        for skill_id, skill_info in jd_skills.items():
            if skill_id not in resume_skills:
                skill_name = skill_info.get("name", "Unknown")
                importance = jd_importance.get(skill_name, "mentioned")
                importance_weight = jd_skills[skill_id].get("importance_weight", 0.5)
                
                missing.append({
                    "id": skill_id,
                    "name": skill_name,
                    "category": skill_info.get("category", "Unknown"),
                    "importance": importance,
                    "importance_weight": importance_weight,
                    "priority": self._get_priority_level(importance)
                })
        
        # Sort by importance weight (highest priority first)
        missing.sort(key=lambda x: x["importance_weight"], reverse=True)
        
        return missing
    
    def _identify_weak_skills(self, resume_skills: Dict, jd_skills: Dict) -> List[Dict]:
        """Identify skills in resume but not required in JD (potentially irrelevant)"""
        weak = []
        
        for skill_id, skill_info in resume_skills.items():
            if skill_id not in jd_skills:
                weak.append({
                    "id": skill_id,
                    "name": skill_info.get("name", "Unknown"),
                    "category": skill_info.get("category", "Unknown")
                })
        
        return weak
    
    def _calculate_match_score(self, matched_skills: List[Dict], missing_skills: List[Dict],
                               jd_skills: Dict, jd_importance: Dict, 
                               similarity_score: float) -> Dict:
        """
        Calculate match score with detailed breakdown
        
        Scoring logic:
        - Required skills matched: 40 points (weight: 1.0 each)
        - Preferred skills matched: 20 points (weight: 0.7 each)
        - Mentioned skills matched: 10 points (weight: 0.5 each)
        - Overall semantic similarity: 30 points
        """
        
        # Initialize scores
        required_matched = 0
        preferred_matched = 0
        mentioned_matched = 0
        required_total = 0
        preferred_total = 0
        mentioned_total = 0
        
        # Count matched skills by importance
        for skill in matched_skills:
            importance = skill["importance"]
            if importance == "required":
                required_matched += 1
            elif importance == "preferred":
                preferred_matched += 1
            else:
                mentioned_matched += 1
        
        # Count total skills in JD by importance
        for skill_name, importance in jd_importance.items():
            if importance == "required":
                required_total += 1
            elif importance == "preferred":
                preferred_total += 1
            else:
                mentioned_total += 1
        
        # Calculate component scores
        required_score = (required_matched / required_total * 40) if required_total > 0 else 0
        preferred_score = (preferred_matched / preferred_total * 20) if preferred_total > 0 else 0
        mentioned_score = (mentioned_matched / mentioned_total * 10) if mentioned_total > 0 else 0
        similarity_component = similarity_score * 30
        
        # Total score (0-100)
        total_score = required_score + preferred_score + mentioned_score + similarity_component
        
        return {
            "total_score": round(total_score, 2),
            "required_skills_score": round(required_score, 2),
            "preferred_skills_score": round(preferred_score, 2),
            "mentioned_skills_score": round(mentioned_score, 2),
            "similarity_score": round(similarity_component, 2),
            "required_matched": required_matched,
            "required_total": required_total,
            "preferred_matched": preferred_matched,
            "preferred_total": preferred_total,
            "mentioned_matched": mentioned_matched,
            "mentioned_total": mentioned_total
        }
    
    def _generate_explanation(self, score_breakdown: Dict, matched_skills: List[Dict],
                             missing_skills: List[Dict], resume_skill_count: int,
                             jd_skill_count: int) -> Dict:
        """Generate human-readable explanation of the match score"""
        
        total_score = score_breakdown["total_score"]
        
        # Determine overall match level
        if total_score >= 80:
            match_level = "Excellent Match"
            recommendation = "Strong candidate - proceed with interview"
        elif total_score >= 60:
            match_level = "Good Match"
            recommendation = "Qualified candidate - consider for interview"
        elif total_score >= 40:
            match_level = "Moderate Match"
            recommendation = "Potential candidate - upskilling recommended"
        else:
            match_level = "Low Match"
            recommendation = "Significant skill gaps - extensive training needed"
        
        # Build detailed explanation
        explanation_parts = []
        
        # Required skills explanation
        req_matched = score_breakdown["required_matched"]
        req_total = score_breakdown["required_total"]
        if req_total > 0:
            req_percentage = (req_matched / req_total * 100)
            explanation_parts.append(
                f"Required Skills: {req_matched}/{req_total} matched ({req_percentage:.0f}%) - "
                f"Contributing {score_breakdown['required_skills_score']:.1f}/40 points"
            )
        
        # Preferred skills explanation
        pref_matched = score_breakdown["preferred_matched"]
        pref_total = score_breakdown["preferred_total"]
        if pref_total > 0:
            pref_percentage = (pref_matched / pref_total * 100)
            explanation_parts.append(
                f"Preferred Skills: {pref_matched}/{pref_total} matched ({pref_percentage:.0f}%) - "
                f"Contributing {score_breakdown['preferred_skills_score']:.1f}/20 points"
            )
        
        # Similarity explanation
        explanation_parts.append(
            f"Semantic Similarity: Contributing {score_breakdown['similarity_score']:.1f}/30 points based on overall resume-JD alignment"
        )
        
        # Missing critical skills
        critical_missing = [s for s in missing_skills if s["importance"] == "required"]
        if critical_missing:
            critical_names = [s["name"] for s in critical_missing[:5]]
            explanation_parts.append(
                f"Critical Gap: Missing {len(critical_missing)} required skill(s) - {', '.join(critical_names)}"
            )
        
        return {
            "match_level": match_level,
            "recommendation": recommendation,
            "details": explanation_parts,
            "summary": f"{match_level}: {req_matched}/{req_total} required skills matched, "
                      f"{len(missing_skills)} skills to develop"
        }
    
    def _get_priority_level(self, importance: str) -> str:
        """Convert importance to priority level"""
        priority_map = {
            "required": "HIGH",
            "preferred": "MEDIUM",
            "mentioned": "LOW"
        }
        return priority_map.get(importance, "LOW")
    
    def _empty_result(self) -> Dict:
        """Return empty result structure"""
        return {
            "match_score": 0.0,
            "match_percentage": 0.0,
            "matched_skills": [],
            "missing_skills": [],
            "weak_skills": [],
            "score_breakdown": {},
            "explanation": {},
            "overall_similarity": 0.0,
            "resume_skill_count": 0,
            "jd_skill_count": 0
        }


# Factory function
def get_skill_gap_analyzer(db: Session) -> SkillGapAnalyzer:
    return SkillGapAnalyzer(db)