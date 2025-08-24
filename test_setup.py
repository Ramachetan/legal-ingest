"""
Test script to validate the Legal Document Ingestion Pipeline setup
Run this script to check if all components are working correctly
"""
import os
import sys
import tempfile
from io import BytesIO

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    try:
        from src.config import Config
        from src.document_loader import DocumentLoader
        from src.text_splitter import LegalTextSplitter
        from src.embedding_generator import GeminiEmbeddingGenerator
        from src.vector_store import FAISSVectorStore
        from src.pipeline import IngestionPipeline
        print("✅ All modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\nTesting configuration...")
    try:
        from src.config import Config
        config = Config()
        
        if not config.GOOGLE_API_KEY or config.GOOGLE_API_KEY == "your_google_api_key_here":
            print("⚠️ Google API key not configured")
            print("   Please set GOOGLE_API_KEY in your .env file")
            return False
        
        print("✅ Configuration loaded successfully")
        print(f"   - Chunk size: {config.CHUNK_SIZE}")
        print(f"   - Chunk overlap: {config.CHUNK_OVERLAP}")
        print(f"   - Embedding model: {config.EMBEDDING_MODEL}")
        print(f"   - Supported formats: {config.SUPPORTED_FORMATS}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_document_loader():
    """Test document loading functionality"""
    print("\nTesting document loader...")
    try:
        from src.document_loader import DocumentLoader
        loader = DocumentLoader()
        
        # Test with a simple text file
        test_content = "This is a test legal document.\n\nSection 1: Introduction\nThis section contains important legal text."
        test_file = BytesIO(test_content.encode('utf-8'))
        
        result = loader.load_document(test_file, "test.txt")
        
        if result and result['text']:
            print("✅ Document loader working correctly")
            print(f"   - Extracted {len(result['text'])} characters")
            return True
        else:
            print("❌ Document loader failed to extract text")
            return False
            
    except Exception as e:
        print(f"❌ Document loader error: {e}")
        return False

def test_text_splitter():
    """Test text splitting functionality"""
    print("\nTesting text splitter...")
    try:
        from src.text_splitter import LegalTextSplitter
        splitter = LegalTextSplitter()
        
        test_text = """
        LEGAL DOCUMENT
        
        Section 1: Introduction
        This is the introduction section of the legal document. It contains important information about the purpose and scope of this document.
        
        Section 2: Terms and Conditions
        This section outlines all the terms and conditions that apply to this agreement. Each clause is carefully crafted to ensure legal compliance.
        
        Article 1: Definitions
        For the purposes of this document, the following terms shall have the meanings assigned to them below.
        """
        
        metadata = {
            'filename': 'test_document.txt',
            'file_type': '.txt'
        }
        
        chunks = splitter.split_text(test_text, metadata)
        
        if chunks and len(chunks) > 0:
            print(f"✅ Text splitter working correctly")
            print(f"   - Generated {len(chunks)} chunks")
            print(f"   - Average chunk size: {sum(len(c['text']) for c in chunks) // len(chunks)} characters")
            return True
        else:
            print("❌ Text splitter failed to generate chunks")
            return False
            
    except Exception as e:
        print(f"❌ Text splitter error: {e}")
        return False

def test_embedding_generator():
    """Test embedding generation (requires valid API key)"""
    print("\nTesting embedding generator...")
    try:
        from src.embedding_generator import GeminiEmbeddingGenerator
        generator = GeminiEmbeddingGenerator()
        
        # Test connection first
        if not generator.test_connection():
            print("❌ Gemini API connection failed")
            print("   Please check your API key and internet connection")
            return False
        
        # Test embedding generation
        test_chunks = [{
            'text': 'This is a test legal document for embedding generation.',
            'chunk_id': 'test_chunk_1',
            'source_document': 'test.txt'
        }]
        
        embedded_chunks = generator.generate_embeddings(test_chunks)
        
        if embedded_chunks and len(embedded_chunks) > 0 and 'embedding' in embedded_chunks[0]:
            embedding_dim = len(embedded_chunks[0]['embedding'])
            print(f"✅ Embedding generator working correctly")
            print(f"   - Generated embedding with {embedding_dim} dimensions")
            return True
        else:
            print("❌ Embedding generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Embedding generator error: {e}")
        return False

def test_vector_store():
    """Test vector store functionality"""
    print("\nTesting vector store...")
    try:
        from src.vector_store import FAISSVectorStore
        import numpy as np
        
        # Use a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Override paths for testing
            os.environ['VECTOR_DB_PATH'] = temp_dir
            os.environ['FAISS_INDEX_PATH'] = os.path.join(temp_dir, 'test_index.index')
            os.environ['METADATA_PATH'] = os.path.join(temp_dir, 'test_metadata.json')
            
            vector_store = FAISSVectorStore()
            
            # Test with dummy embeddings
            test_chunks = [{
                'text': 'Test legal text for vector storage',
                'chunk_id': 'test_chunk_1',
                'source_document': 'test.txt',
                'embedding': np.random.rand(768).tolist()  # Dummy embedding
            }]
            
            success = vector_store.add_embeddings(test_chunks)
            
            if success:
                stats = vector_store.get_stats()
                print(f"✅ Vector store working correctly")
                print(f"   - Stored {stats.get('total_vectors', 0)} vectors")
                print(f"   - Dimension: {stats.get('dimension', 'N/A')}")
                return True
            else:
                print("❌ Vector store failed to add embeddings")
                return False
                
    except Exception as e:
        print(f"❌ Vector store error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Legal Document Ingestion Pipeline - Setup Test")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_configuration,
        test_document_loader,
        test_text_splitter,
        test_embedding_generator,
        test_vector_store
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print("=" * 60)
    print(f"🏆 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Your setup is ready to use.")
        print("\nNext steps:")
        print("1. Run 'streamlit run app.py' to start the web interface")
        print("2. Upload legal documents through the web interface")
        print("3. Monitor the ingestion process and results")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon solutions:")
        print("1. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("2. Set up your .env file with a valid Google API key")
        print("3. Check that your Python environment is activated")
    
    return passed == total

if __name__ == "__main__":
    main()
