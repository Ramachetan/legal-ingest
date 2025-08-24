"""
Embedding generation module using Google Gemini Pro
"""
import logging
import time
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from src.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiEmbeddingGenerator:
    """
    Handles embedding generation using Google Gemini Pro
    """
    
    def __init__(self):
        self.config = Config()
        self._configure_gemini()
        
        # Rate limiting parameters
        self.rate_limit_delay = 1.0  # seconds between requests
        self.max_retries = 3
        self.retry_delay = 2.0  # seconds
    
    def _configure_gemini(self):
        """Configure Gemini API with the provided API key"""
        try:
            if not self.config.GOOGLE_API_KEY:
                raise ValueError("Google API key not found in configuration")
            
            genai.configure(api_key=self.config.GOOGLE_API_KEY)
            logger.info("Gemini API configured successfully")
            
        except Exception as e:
            logger.error(f"Error configuring Gemini API: {str(e)}")
            raise
    
    def generate_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for a list of text chunks
        
        Args:
            chunks: List of chunk dictionaries containing text and metadata
            
        Returns:
            List of chunk dictionaries with added embeddings
        """
        try:
            if not chunks:
                return []
            
            embedded_chunks = []
            total_chunks = len(chunks)
            
            logger.info(f"Starting embedding generation for {total_chunks} chunks")
            
            for i, chunk in enumerate(chunks):
                try:
                    # Generate embedding for this chunk
                    embedding = self._get_single_embedding(chunk['text'])
                    
                    if embedding is not None:
                        # Add embedding to chunk
                        chunk['embedding'] = embedding
                        chunk['embedding_model'] = self.config.EMBEDDING_MODEL
                        chunk['embedding_dimension'] = len(embedding)
                        embedded_chunks.append(chunk)
                        
                        logger.info(f"Generated embedding for chunk {i+1}/{total_chunks}")
                    else:
                        logger.warning(f"Failed to generate embedding for chunk {i+1}")
                    
                    # Rate limiting
                    if i < total_chunks - 1:  # Don't delay after the last chunk
                        time.sleep(self.rate_limit_delay)
                    
                except Exception as e:
                    logger.error(f"Error processing chunk {i+1}: {str(e)}")
                    continue
            
            logger.info(f"Successfully generated embeddings for {len(embedded_chunks)}/{total_chunks} chunks")
            return embedded_chunks
            
        except Exception as e:
            logger.error(f"Error in batch embedding generation: {str(e)}")
            return []
    
    def _get_single_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text chunk with retry logic
        
        Args:
            text: Text content to embed
            
        Returns:
            List of floats representing the embedding or None if failed
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return None
        
        for attempt in range(self.max_retries):
            try:
                # Generate embedding using Gemini
                result = genai.embed_content(
                    model=self.config.EMBEDDING_MODEL,
                    content=text,
                    task_type=self.config.EMBEDDING_TASK_TYPE
                )
                
                # Extract embedding from result
                if 'embedding' in result:
                    embedding = result['embedding']
                    if embedding and len(embedding) > 0:
                        return embedding
                    else:
                        logger.warning("Empty embedding returned from Gemini")
                        return None
                else:
                    logger.warning("No embedding found in Gemini response")
                    return None
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                else:
                    logger.error(f"All {self.max_retries} attempts failed for text chunk")
                    return None
        
        return None
    
    def test_connection(self) -> bool:
        """
        Test the connection to Gemini API
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            test_text = "This is a test sentence for embedding generation."
            result = self._get_single_embedding(test_text)
            
            if result is not None:
                logger.info("Gemini API connection test successful")
                return True
            else:
                logger.error("Gemini API connection test failed")
                return False
                
        except Exception as e:
            logger.error(f"Gemini API connection test failed: {str(e)}")
            return False
