"""
Text chunking module for legal documents
Implements recursive character text splitter optimized for legal content
"""
import re
import logging
from typing import List, Dict, Any
from src.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalTextSplitter:
    """
    Text splitter specifically designed for legal documents
    Uses hierarchical splitting to maintain semantic coherence
    """
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.config = Config()
        self.chunk_size = chunk_size or self.config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or self.config.CHUNK_OVERLAP
        
        # Legal document separators in order of preference
        self.separators = [
            "\n\n\n",  # Multiple line breaks (section breaks)
            "\n\n",    # Double line breaks (paragraph breaks)
            "\n",      # Single line breaks
            ". ",      # Sentence endings
            ", ",      # Clause separators
            " ",       # Word boundaries
            ""         # Character level (last resort)
        ]
        
        # Legal document patterns for intelligent splitting
        self.legal_patterns = {
            'section': r'(?i)(section|sec\.?|§)\s*\d+',
            'article': r'(?i)(article|art\.?)\s*\d+',
            'clause': r'(?i)(clause|cl\.?)\s*\d+',
            'paragraph': r'(?i)(paragraph|para\.?|¶)\s*\d+',
            'subsection': r'(?i)(subsection|subsec\.?)\s*\d+',
            'chapter': r'(?i)(chapter|ch\.?)\s*\d+',
            'part': r'(?i)(part|pt\.?)\s*\d+',
        }
    
    def split_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split text into chunks optimized for legal documents
        
        Args:
            text: Input text to split
            metadata: Original document metadata
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        try:
            if not text or not text.strip():
                return []
            
            # Clean and normalize text
            text = self._clean_text(text)
            
            # Split text using recursive approach
            chunks = self._recursive_split(text)
            
            # Create chunk objects with metadata
            chunk_objects = []
            for i, chunk_text in enumerate(chunks):
                if chunk_text.strip():  # Only add non-empty chunks
                    chunk_obj = {
                        'text': chunk_text.strip(),
                        'chunk_id': f"{metadata['filename']}_chunk_{i}",
                        'chunk_index': i,
                        'source_document': metadata['filename'],
                        'file_type': metadata['file_type'],
                        'char_count': len(chunk_text),
                        'legal_sections': self._identify_legal_sections(chunk_text)
                    }
                    chunk_objects.append(chunk_obj)
            
            logger.info(f"Split document {metadata['filename']} into {len(chunk_objects)} chunks")
            return chunk_objects
            
        except Exception as e:
            logger.error(f"Error splitting text: {str(e)}")
            return []
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for better processing"""
        # Remove excessive whitespace while preserving structure
        text = re.sub(r'\n\s*\n\s*\n', '\n\n\n', text)  # Normalize section breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Normalize paragraph breaks
        text = re.sub(r'[ \t]+', ' ', text)  # Normalize spaces and tabs
        text = re.sub(r'\r\n', '\n', text)  # Normalize line endings
        
        return text.strip()
    
    def _recursive_split(self, text: str, depth: int = 0, max_depth: int = 10) -> List[str]:
        """
        Recursively split text using hierarchical separators
        
        Args:
            text: Text to split
            depth: Current recursion depth
            max_depth: Maximum allowed recursion depth
        """
        # Prevent infinite recursion
        if depth >= max_depth:
            logger.warning(f"Maximum recursion depth reached, falling back to character splitting")
            return self._split_by_length(text)
        
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []
        
        # Try each separator in order
        for separator in self.separators:
            if separator in text:
                chunks = self._split_by_separator(text, separator)
                
                # Check if we made meaningful progress (at least 10% reduction in largest chunk)
                max_chunk_size = max(len(chunk) for chunk in chunks) if chunks else len(text)
                if max_chunk_size >= len(text) * 0.9:
                    # No meaningful progress, try next separator
                    continue
                
                # Process each chunk recursively if needed
                final_chunks = []
                for chunk in chunks:
                    if len(chunk) <= self.chunk_size:
                        final_chunks.append(chunk)
                    else:
                        # Recursively split oversized chunks with increased depth
                        sub_chunks = self._recursive_split(chunk, depth + 1, max_depth)
                        final_chunks.extend(sub_chunks)
                
                return final_chunks
        
        # If no separators work, split by character count
        return self._split_by_length(text)
    
    def _split_by_separator(self, text: str, separator: str) -> List[str]:
        """Split text by a specific separator with overlap handling"""
        if separator == "":
            return self._split_by_length(text)
        
        parts = text.split(separator)
        
        # If separator doesn't split effectively (only 1 or 2 parts), return empty list
        # This prevents infinite recursion when separators don't help
        if len(parts) <= 2 and len(text) > self.chunk_size:
            return []
        
        chunks = []
        current_chunk = ""
        
        for i, part in enumerate(parts):
            # Add separator back except for the last part
            if i > 0:
                part = separator + part
            
            # Check if adding this part exceeds chunk size
            if len(current_chunk) + len(part) <= self.chunk_size:
                current_chunk += part
            else:
                # Save current chunk if it's not empty
                if current_chunk.strip():
                    chunks.append(current_chunk)
                
                # Start new chunk with overlap if applicable
                current_chunk = self._get_overlap(current_chunk) + part
        
        # Add the final chunk
        if current_chunk.strip():
            chunks.append(current_chunk)
        
        return chunks
    
    def _split_by_length(self, text: str) -> List[str]:
        """Split text by character length as last resort"""
        if not text.strip():
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            if end >= len(text):
                chunk = text[start:]
                if chunk.strip():
                    chunks.append(chunk)
                break
            
            # Try to find a good breaking point near the end
            chunk = text[start:end]
            
            # Look for sentence boundary in the last 30% of the chunk
            search_start = max(0, int(self.chunk_size * 0.7))
            last_period = chunk.rfind('. ', search_start)
            
            if last_period > search_start:  # If we find a period in the last 30%
                end = start + last_period + 2
                chunk = text[start:end]
            
            if chunk.strip():
                chunks.append(chunk)
            
            # Move start position with overlap, ensuring we make progress
            next_start = max(start + 1, end - self.chunk_overlap)
            start = next_start
        
        return chunks
    
    def _get_overlap(self, chunk: str) -> str:
        """Get overlap text from the end of a chunk"""
        if len(chunk) <= self.chunk_overlap:
            return chunk
        
        overlap_text = chunk[-self.chunk_overlap:]
        
        # Try to start overlap at a sentence boundary
        first_period = overlap_text.find('. ')
        if first_period != -1:
            return overlap_text[first_period + 2:]
        
        return overlap_text
    
    def _identify_legal_sections(self, text: str) -> List[str]:
        """Identify legal section types in the text"""
        sections = []
        
        for section_type, pattern in self.legal_patterns.items():
            if re.search(pattern, text):
                sections.append(section_type)
        
        return sections
