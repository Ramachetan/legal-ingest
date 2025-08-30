"""
Configuration module for the Legal Document Ingestion Pipeline
"""
import os
from dotenv import load_dotenv

# Load environment variables for local development
load_dotenv()

def _get_config_value(key, default=None, section=None):
    """Get configuration value from Streamlit secrets or environment variables"""
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and st.secrets:
            if section and section in st.secrets:
                return st.secrets[section].get(key, default)
            elif key in st.secrets:
                return st.secrets[key]
    except ImportError:
        pass
    
    # Fall back to environment variables
    return os.getenv(key, default)

class Config:
    """Configuration class for the application"""
    
    # Google API Configuration
    GOOGLE_API_KEY = _get_config_value('GOOGLE_API_KEY', section='google')
    
    # Vector Database Configuration
    VECTOR_DB_PATH = _get_config_value('VECTOR_DB_PATH', './vector_store', section='vector_db')
    FAISS_INDEX_PATH = _get_config_value('FAISS_INDEX_PATH', './vector_store/faiss_index.index', section='vector_db')
    METADATA_PATH = _get_config_value('METADATA_PATH', './vector_store/metadata.json', section='vector_db')
    
    # Text Processing Configuration
    CHUNK_SIZE = int(_get_config_value('CHUNK_SIZE', 1000, section='text_processing'))
    CHUNK_OVERLAP = int(_get_config_value('CHUNK_OVERLAP', 200, section='text_processing'))
    MAX_FILE_SIZE_MB = int(_get_config_value('MAX_FILE_SIZE_MB', 50, section='text_processing'))
    
    # Gemini Model Configuration
    EMBEDDING_MODEL = _get_config_value('EMBEDDING_MODEL', 'models/embedding-001', section='gemini')
    EMBEDDING_TASK_TYPE = _get_config_value('EMBEDDING_TASK_TYPE', 'retrieval_document', section='gemini')
    
    # Supported file formats
    SUPPORTED_FORMATS = ['.pdf', '.docx', '.txt']
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required. Please set it in your .env file (local) or secrets.toml (Streamlit Cloud)")
        
        # Create vector store directory if it doesn't exist
        os.makedirs(cls.VECTOR_DB_PATH, exist_ok=True)
        
        return True
