from sentence_transformers import SentenceTransformer
import logging
from typing import List, Optional
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generate embeddings using Hugging Face Sentence Transformers"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding model
        Args:
            model_name: Hugging Face model name (default: all-MiniLM-L6-v2)
        """
        try:
            logger.info(f"Loading embedding model: {model_name}")
            self.model = SentenceTransformer(model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text
        Args:
            text: Input text to embed
        Returns:
            List of floats representing the embedding vector
        """
        try:
            if not text or not text.strip():
                logger.warning("Empty text provided for embedding")
                return None
            
            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            
            # Convert numpy array to list for JSON storage
            return embedding.tolist()
        
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return None
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts
        Args:
            texts: List of texts to embed
        Returns:
            List of embedding vectors
        """
        try:
            if not texts:
                return []
            
            # Filter out empty texts
            valid_texts = [t for t in texts if t and t.strip()]
            
            if not valid_texts:
                return [None] * len(texts)
            
            # Generate embeddings in batch
            embeddings = self.model.encode(valid_texts, convert_to_numpy=True)
            
            # Convert to list format
            return [emb.tolist() for emb in embeddings]
        
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            return [None] * len(texts)


# Singleton instance
embedding_service = EmbeddingService()
