import numpy as np
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class SimilarityCalculator:
    """Calculate cosine similarity between embeddings"""
    
    @staticmethod
    def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between 0 and 1 (1 = identical)
        """
        try:
            if not embedding1 or not embedding2:
                logger.warning("Empty embedding provided")
                return 0.0
            
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Check if dimensions match
            if vec1.shape != vec2.shape:
                logger.error(f"Embedding dimension mismatch: {vec1.shape} vs {vec2.shape}")
                return 0.0
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            
            # Clamp to [0, 1] range (cosine similarity can be -1 to 1)
            similarity = max(0.0, min(1.0, similarity))
            
            return float(similarity)
        
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            return 0.0
    
    @staticmethod
    def calculate_resume_jd_similarity(resume_embedding: Optional[List[float]], 
                                       jd_embedding: Optional[List[float]]) -> Dict[str, float]:
        """
        Calculate similarity between resume and job description
        
        Args:
            resume_embedding: Resume embedding vector
            jd_embedding: Job description embedding vector
            
        Returns:
            Dict with similarity_score (0-1) and percentage (0-100)
        """
        if not resume_embedding or not jd_embedding:
            return {
                "similarity_score": 0.0,
                "similarity_percentage": 0.0
            }
        
        similarity = SimilarityCalculator.cosine_similarity(resume_embedding, jd_embedding)
        
        return {
            "similarity_score": round(similarity, 4),
            "similarity_percentage": round(similarity * 100, 2)
        }
    
    @staticmethod
    def find_most_similar_jds(resume_embedding: List[float], 
                             jd_embeddings: List[Dict]) -> List[Dict]:
        """
        Find most similar job descriptions to a resume
        
        Args:
            resume_embedding: Resume embedding vector
            jd_embeddings: List of dicts with {id, title, embedding}
            
        Returns:
            Sorted list of JDs with similarity scores (highest first)
        """
        results = []
        
        for jd in jd_embeddings:
            if not jd.get("embedding"):
                continue
            
            similarity = SimilarityCalculator.cosine_similarity(
                resume_embedding, 
                jd["embedding"]
            )
            
            results.append({
                "jd_id": jd["id"],
                "title": jd.get("title", "Unknown"),
                "similarity_score": round(similarity, 4),
                "similarity_percentage": round(similarity * 100, 2)
            })
        
        # Sort by similarity (highest first)
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return results
    
    @staticmethod
    def find_most_similar_resumes(jd_embedding: List[float], 
                                 resume_embeddings: List[Dict]) -> List[Dict]:
        """
        Find most similar resumes to a job description
        
        Args:
            jd_embedding: Job description embedding vector
            resume_embeddings: List of dicts with {id, user_id, embedding}
            
        Returns:
            Sorted list of resumes with similarity scores (highest first)
        """
        results = []
        
        for resume in resume_embeddings:
            if not resume.get("embedding"):
                continue
            
            similarity = SimilarityCalculator.cosine_similarity(
                jd_embedding, 
                resume["embedding"]
            )
            
            results.append({
                "resume_id": resume["id"],
                "user_id": resume.get("user_id"),
                "similarity_score": round(similarity, 4),
                "similarity_percentage": round(similarity * 100, 2)
            })
        
        # Sort by similarity (highest first)
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return results


# Singleton instance
similarity_calculator = SimilarityCalculator()
