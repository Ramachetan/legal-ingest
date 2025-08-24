"""
Configuration module for the Legal Document Ingestion Pipeline
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the application"""
    
    # Google API Configuration
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    # Vector Database Configuration
    VECTOR_DB_PATH = os.getenv('VECTOR_DB_PATH', './vector_store')
    FAISS_INDEX_PATH = os.getenv('FAISS_INDEX_PATH', './vector_store/faiss_index.index')
    METADATA_PATH = os.getenv('METADATA_PATH', './vector_store/metadata.json')
    
    # Text Processing Configuration
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 1000))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 200))
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 50))
    
    # Gemini Model Configuration
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'models/embedding-001')
    EMBEDDING_TASK_TYPE = os.getenv('EMBEDDING_TASK_TYPE', 'retrieval_document')
    
    # Supported file formats
    SUPPORTED_FORMATS = ['.pdf', '.docx', '.txt']
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        # Create vector store directory if it doesn't exist
        os.makedirs(cls.VECTOR_DB_PATH, exist_ok=True)
        
        return True
