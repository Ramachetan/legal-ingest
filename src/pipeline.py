"""
Main ingestion pipeline orchestrator
Coordinates the document processing workflow
"""
import logging
import os
from typing import List, Dict, Any, Optional
from io import BytesIO

from src.config import Config
from src.document_loader import DocumentLoader
from src.text_splitter import LegalTextSplitter
from src.embedding_generator import GeminiEmbeddingGenerator
from src.vector_store import FAISSVectorStore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IngestionPipeline:
    """
    Main pipeline for ingesting legal documents into the vector store
    """
    
    def __init__(self):
        self.config = Config()
        
        # Initialize components
        self.document_loader = DocumentLoader()
        self.text_splitter = LegalTextSplitter()
        self.embedding_generator = GeminiEmbeddingGenerator()
        self.vector_store = FAISSVectorStore()
        
        # Validate configuration
        self._validate_setup()
    
    def _validate_setup(self):
        """Validate that all components are properly configured"""
        try:
            # Validate configuration
            self.config.validate_config()
            
            # Test embedding generator connection
            if not self.embedding_generator.test_connection():
                raise ValueError("Failed to connect to Gemini API")
            
            logger.info("Pipeline setup validated successfully")
            
        except Exception as e:
            logger.error(f"Pipeline setup validation failed: {str(e)}")
            raise
    
    def ingest_documents(self, uploaded_files: List[Dict[str, Any]], 
                        progress_callback=None) -> Dict[str, Any]:
        """
        Main ingestion workflow for uploaded documents
        
        Args:
            uploaded_files: List of uploaded file objects with 'name' and 'data' keys
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Dictionary containing ingestion results and statistics
        """
        results = {
            'success': True,
            'processed_documents': [],
            'failed_documents': [],
            'total_chunks': 0,
            'total_embeddings': 0,
            'error_messages': []
        }
        
        try:
            total_files = len(uploaded_files)
            logger.info(f"Starting ingestion of {total_files} documents")
            
            for i, file_info in enumerate(uploaded_files):
                try:
                    if progress_callback:
                        progress_callback(
                            f"Processing document {i+1}/{total_files}: {file_info['name']}", 
                            (i / total_files) * 100
                        )
                    
                    # Process single document
                    doc_result = self._process_single_document(file_info)
                    
                    if doc_result['success']:
                        results['processed_documents'].append(doc_result)
                        results['total_chunks'] += doc_result['chunk_count']
                        results['total_embeddings'] += doc_result['embedding_count']
                    else:
                        results['failed_documents'].append(doc_result)
                        results['error_messages'].extend(doc_result['errors'])
                    
                except Exception as e:
                    error_msg = f"Error processing {file_info['name']}: {str(e)}"
                    logger.error(error_msg)
                    results['failed_documents'].append({
                        'filename': file_info['name'],
                        'success': False,
                        'errors': [error_msg]
                    })
                    results['error_messages'].append(error_msg)
            
            # Final progress update
            if progress_callback:
                progress_callback("Ingestion completed", 100)
            
            # Update success status
            results['success'] = len(results['failed_documents']) == 0
            
            logger.info(f"Ingestion completed. Success: {len(results['processed_documents'])}, "
                       f"Failed: {len(results['failed_documents'])}")
            
            return results
            
        except Exception as e:
            error_msg = f"Pipeline ingestion failed: {str(e)}"
            logger.error(error_msg)
            results['success'] = False
            results['error_messages'].append(error_msg)
            return results
    
    def _process_single_document(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single document through the entire pipeline
        
        Args:
            file_info: Dictionary with 'name' and 'data' keys
            
        Returns:
            Dictionary containing processing results
        """
        doc_result = {
            'filename': file_info['name'],
            'success': False,
            'chunk_count': 0,
            'embedding_count': 0,
            'errors': []
        }
        
        try:
            # Step 1: Load and extract text
            logger.info(f"Loading document: {file_info['name']}")
            file_data = BytesIO(file_info['data'])
            document_data = self.document_loader.load_document(file_data, file_info['name'])
            
            if not document_data:
                raise ValueError("Failed to extract text from document")
            
            # Step 2: Split text into chunks
            logger.info(f"Splitting text for: {file_info['name']}")
            chunks = self.text_splitter.split_text(document_data['text'], document_data)
            
            if not chunks:
                raise ValueError("No text chunks generated from document")
            
            doc_result['chunk_count'] = len(chunks)
            
            # Step 3: Generate embeddings
            logger.info(f"Generating embeddings for: {file_info['name']}")
            embedded_chunks = self.embedding_generator.generate_embeddings(chunks)
            
            if not embedded_chunks:
                raise ValueError("No embeddings generated from chunks")
            
            doc_result['embedding_count'] = len(embedded_chunks)
            
            # Step 4: Store in vector database
            logger.info(f"Storing embeddings for: {file_info['name']}")
            if not self.vector_store.add_embeddings(embedded_chunks):
                raise ValueError("Failed to store embeddings in vector database")
            
            doc_result['success'] = True
            logger.info(f"Successfully processed: {file_info['name']}")
            
        except Exception as e:
            error_msg = f"Error processing {file_info['name']}: {str(e)}"
            logger.error(error_msg)
            doc_result['errors'].append(error_msg)
        
        return doc_result
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """
        Get current status and statistics of the pipeline
        
        Returns:
            Dictionary containing pipeline status information
        """
        try:
            return {
                'vector_store_stats': self.vector_store.get_stats(),
                'stored_documents': self.vector_store.list_documents(),
                'config': {
                    'chunk_size': self.config.CHUNK_SIZE,
                    'chunk_overlap': self.config.CHUNK_OVERLAP,
                    'embedding_model': self.config.EMBEDDING_MODEL,
                    'supported_formats': self.config.SUPPORTED_FORMATS
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting pipeline status: {str(e)}")
            return {
                'error': str(e),
                'vector_store_stats': {},
                'stored_documents': [],
                'config': {}
            }
    
    def clear_all_data(self) -> bool:
        """
        Clear all data from the pipeline
        
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.vector_store.clear_all()
        except Exception as e:
            logger.error(f"Error clearing pipeline data: {str(e)}")
            return False
