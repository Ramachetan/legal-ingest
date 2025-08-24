"""
FAISS-based vector store for storing and retrieving document embeddings
"""
import os
import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional
import faiss
from src.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FAISSVectorStore:
    """
    FAISS-based vector store for document embeddings with metadata support
    """
    
    def __init__(self):
        self.config = Config()
        self.index = None
        self.metadata = []
        self.dimension = None
        
        # Load existing index if available
        self._load_existing_index()
    
    def _load_existing_index(self):
        """Load existing FAISS index and metadata if available"""
        try:
            if os.path.exists(self.config.FAISS_INDEX_PATH):
                self.index = faiss.read_index(self.config.FAISS_INDEX_PATH)
                self.dimension = self.index.d
                logger.info(f"Loaded existing FAISS index with dimension {self.dimension}")
                
                # Load metadata
                if os.path.exists(self.config.METADATA_PATH):
                    with open(self.config.METADATA_PATH, 'r', encoding='utf-8') as f:
                        self.metadata = json.load(f)
                    logger.info(f"Loaded {len(self.metadata)} metadata entries")
                else:
                    self.metadata = []
            else:
                logger.info("No existing FAISS index found")
                
        except Exception as e:
            logger.error(f"Error loading existing index: {str(e)}")
            self.index = None
            self.metadata = []
    
    def add_embeddings(self, embedded_chunks: List[Dict[str, Any]]) -> bool:
        """
        Add embeddings to the vector store
        
        Args:
            embedded_chunks: List of chunk dictionaries with embeddings
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not embedded_chunks:
                logger.warning("No embedded chunks provided")
                return False
            
            # Extract embeddings and prepare metadata
            embeddings = []
            chunk_metadata = []
            
            for chunk in embedded_chunks:
                if 'embedding' in chunk and chunk['embedding']:
                    embeddings.append(chunk['embedding'])
                    
                    # Prepare metadata (exclude embedding for storage)
                    metadata_entry = {k: v for k, v in chunk.items() if k != 'embedding'}
                    chunk_metadata.append(metadata_entry)
            
            if not embeddings:
                logger.warning("No valid embeddings found in chunks")
                return False
            
            # Convert to numpy array
            embeddings_array = np.array(embeddings, dtype=np.float32)
            
            # Initialize index if it doesn't exist
            if self.index is None:
                self.dimension = embeddings_array.shape[1]
                self.index = faiss.IndexFlatL2(self.dimension)  # L2 distance
                logger.info(f"Created new FAISS index with dimension {self.dimension}")
            
            # Verify dimension consistency
            if embeddings_array.shape[1] != self.dimension:
                raise ValueError(f"Embedding dimension mismatch: expected {self.dimension}, got {embeddings_array.shape[1]}")
            
            # Add embeddings to index
            start_id = len(self.metadata)  # Starting ID for new chunks
            self.index.add(embeddings_array)
            
            # Add metadata with IDs
            for i, metadata_entry in enumerate(chunk_metadata):
                metadata_entry['vector_id'] = start_id + i
                self.metadata.append(metadata_entry)
            
            logger.info(f"Added {len(embeddings)} embeddings to vector store")
            
            # Save updated index and metadata
            self._save_index()
            self._save_metadata()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding embeddings to vector store: {str(e)}")
            return False
    
    def search(self, query_embedding: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents using query embedding
        
        Args:
            query_embedding: Query embedding vector
            k: Number of similar documents to return
            
        Returns:
            List of similar documents with metadata and scores
        """
        try:
            if self.index is None:
                logger.warning("No index available for search")
                return []
            
            if not query_embedding:
                logger.warning("Empty query embedding provided")
                return []
            
            # Convert to numpy array
            query_vector = np.array([query_embedding], dtype=np.float32)
            
            # Verify dimension
            if query_vector.shape[1] != self.dimension:
                raise ValueError(f"Query dimension mismatch: expected {self.dimension}, got {query_vector.shape[1]}")
            
            # Perform search
            distances, indices = self.index.search(query_vector, k)
            
            # Prepare results
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.metadata):
                    result = self.metadata[idx].copy()
                    result['similarity_score'] = float(distance)
                    result['rank'] = i + 1
                    results.append(result)
            
            logger.info(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store
        
        Returns:
            Dictionary containing store statistics
        """
        try:
            stats = {
                'total_vectors': len(self.metadata) if self.metadata else 0,
                'dimension': self.dimension,
                'index_exists': self.index is not None,
                'unique_documents': len(set(item.get('source_document', '') for item in self.metadata)) if self.metadata else 0
            }
            
            if self.metadata:
                # Document type distribution
                doc_types = {}
                for item in self.metadata:
                    file_type = item.get('file_type', 'unknown')
                    doc_types[file_type] = doc_types.get(file_type, 0) + 1
                stats['document_types'] = doc_types
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting vector store stats: {str(e)}")
            return {}
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all documents in the vector store
        
        Returns:
            List of unique documents with summary information
        """
        try:
            if not self.metadata:
                return []
            
            # Group by source document
            documents = {}
            for item in self.metadata:
                doc_name = item.get('source_document', 'unknown')
                if doc_name not in documents:
                    documents[doc_name] = {
                        'filename': doc_name,
                        'file_type': item.get('file_type', 'unknown'),
                        'chunk_count': 0,
                        'total_chars': 0
                    }
                
                documents[doc_name]['chunk_count'] += 1
                documents[doc_name]['total_chars'] += item.get('char_count', 0)
            
            return list(documents.values())
            
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            return []
    
    def _save_index(self):
        """Save FAISS index to disk"""
        try:
            if self.index is not None:
                faiss.write_index(self.index, self.config.FAISS_INDEX_PATH)
                logger.info("FAISS index saved successfully")
        except Exception as e:
            logger.error(f"Error saving FAISS index: {str(e)}")
    
    def _save_metadata(self):
        """Save metadata to disk"""
        try:
            with open(self.config.METADATA_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
            logger.info("Metadata saved successfully")
        except Exception as e:
            logger.error(f"Error saving metadata: {str(e)}")
    
    def clear_all(self) -> bool:
        """
        Clear all data from the vector store
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Clear in-memory data
            self.index = None
            self.metadata = []
            self.dimension = None
            
            # Remove files
            if os.path.exists(self.config.FAISS_INDEX_PATH):
                os.remove(self.config.FAISS_INDEX_PATH)
            
            if os.path.exists(self.config.METADATA_PATH):
                os.remove(self.config.METADATA_PATH)
            
            logger.info("Vector store cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing vector store: {str(e)}")
            return False
