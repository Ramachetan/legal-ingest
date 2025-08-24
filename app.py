"""
Streamlit Web Application for Legal Document Ingestion Pipeline
"""
import streamlit as st
import os
import sys
import time
from typing import List, Dict, Any

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


try:
    from src.pipeline import IngestionPipeline
    from src.config import Config
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure all dependencies are installed and the src directory is properly configured.")
    st.stop()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d1fae5;
        border: 1px solid #10b981;
        color: #065f46;
    }
    .error-box {
        background-color: #fef2f2;
        border: 1px solid #ef4444;
        color: #991b1b;
    }
    .info-box {
        background-color: #dbeafe;
        border: 1px solid #3b82f6;
        color: #1e40af;
    }
    .metric-card {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e2e8f0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'pipeline' not in st.session_state:
        st.session_state.pipeline = None
    if 'pipeline_initialized' not in st.session_state:
        st.session_state.pipeline_initialized = False
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'last_results' not in st.session_state:
        st.session_state.last_results = None

def initialize_pipeline():
    """Initialize the ingestion pipeline"""
    try:
        with st.spinner("Initializing pipeline..."):
            # Validate environment variables
            config = Config()
            if not config.GOOGLE_API_KEY or config.GOOGLE_API_KEY == "your_google_api_key_here":
                st.error("❌ Google API key not configured. Please set GOOGLE_API_KEY in your .env file.")
                st.info("💡 Copy .env.example to .env and add your Google API key.")
                return False
            
            # Initialize pipeline
            pipeline = IngestionPipeline()
            st.session_state.pipeline = pipeline
            st.session_state.pipeline_initialized = True
            
            st.success("✅ Pipeline initialized successfully!")
            return True
            
    except Exception as e:
        st.error(f"❌ Failed to initialize pipeline: {str(e)}")
        st.info("Please check your configuration and API key.")
        return False

def display_file_uploader():
    """Display file upload interface"""
    st.subheader("📄 Upload Legal Documents")
    
    uploaded_files = st.file_uploader(
        "Choose legal documents to ingest",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        help="Supported formats: PDF, DOCX, TXT. Maximum file size: 50MB per file."
    )
    
    if uploaded_files:
        st.write(f"📋 **{len(uploaded_files)} file(s) selected:**")
        for file in uploaded_files:
            file_size = len(file.getvalue()) / (1024 * 1024)  # Convert to MB
            st.write(f"• {file.name} ({file_size:.1f} MB)")
    
    return uploaded_files

def process_documents(uploaded_files):
    """Process uploaded documents through the pipeline"""
    if not uploaded_files:
        st.warning("Please select files to process.")
        return
    
    if st.session_state.processing:
        st.warning("Processing in progress. Please wait...")
        return
    
    if st.button("🚀 Start Ingestion Process", type="primary", disabled=st.session_state.processing):
        st.session_state.processing = True
        
        # Prepare file data
        file_data = []
        for file in uploaded_files:
            file_data.append({
                'name': file.name,
                'data': file.getvalue()
            })
        
        # Create progress containers
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def progress_callback(message, percentage):
            progress_bar.progress(int(percentage) / 100)
            status_text.text(message)
        
        try:
            # Process documents
            with st.spinner("Processing documents..."):
                results = st.session_state.pipeline.ingest_documents(
                    file_data, 
                    progress_callback=progress_callback
                )
            
            st.session_state.last_results = results
            st.session_state.processing = False
            
            # Display results
            display_processing_results(results)
            
        except Exception as e:
            st.session_state.processing = False
            st.error(f"❌ Processing failed: {str(e)}")

def display_processing_results(results: Dict[str, Any]):
    """Display the results of document processing"""
    st.subheader("📊 Processing Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(results['processed_documents'])}</h3>
            <p>Documents Processed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(results['failed_documents'])}</h3>
            <p>Documents Failed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{results['total_chunks']}</h3>
            <p>Text Chunks</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{results['total_embeddings']}</h3>
            <p>Embeddings Generated</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Success/Error summary
    if results['success']:
        st.markdown(f"""
        <div class="status-box success-box">
            <h4>✅ All documents processed successfully!</h4>
            <p>All {len(results['processed_documents'])} documents have been ingested into the vector database.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="status-box error-box">
            <h4>⚠️ Some documents failed to process</h4>
            <p>{len(results['processed_documents'])} succeeded, {len(results['failed_documents'])} failed.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed results
    if results['processed_documents']:
        st.subheader("✅ Successfully Processed Documents")
        for doc in results['processed_documents']:
            with st.expander(f"📄 {doc['filename']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Chunks Generated:** {doc['chunk_count']}")
                with col2:
                    st.write(f"**Embeddings Created:** {doc['embedding_count']}")
    
    if results['failed_documents']:
        st.subheader("❌ Failed Documents")
        for doc in results['failed_documents']:
            with st.expander(f"⚠️ {doc['filename']}"):
                st.write("**Errors:**")
                for error in doc['errors']:
                    st.write(f"• {error}")

def display_vector_store_status():
    """Display current vector store status and statistics"""
    if not st.session_state.pipeline_initialized:
        return
    
    st.subheader("💾 Vector Store Status")
    
    try:
        status = st.session_state.pipeline.get_pipeline_status()
        stats = status['vector_store_stats']
        documents = status['stored_documents']
        
        # Statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Vectors", stats.get('total_vectors', 0))
        with col2:
            st.metric("Unique Documents", stats.get('unique_documents', 0))
        with col3:
            st.metric("Vector Dimension", stats.get('dimension', 'N/A'))
        
        # Document types distribution
        if 'document_types' in stats:
            st.subheader("📋 Document Types")
            doc_types = stats['document_types']
            for file_type, count in doc_types.items():
                st.write(f"**{file_type.upper()}:** {count} documents")
        
        # Stored documents list
        if documents:
            st.subheader("📚 Stored Documents")
            for doc in documents:
                with st.expander(f"📄 {doc['filename']}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Type:** {doc['file_type'].upper()}")
                    with col2:
                        st.write(f"**Chunks:** {doc['chunk_count']}")
                    with col3:
                        st.write(f"**Characters:** {doc['total_chars']:,}")
        
        # Clear data option
        if st.button("🗑️ Clear All Data", type="secondary"):
            if st.confirm("Are you sure you want to clear all stored documents and embeddings?"):
                with st.spinner("Clearing data..."):
                    if st.session_state.pipeline.clear_all_data():
                        st.success("✅ All data cleared successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to clear data.")
        
    except Exception as e:
        st.error(f"Error loading vector store status: {str(e)}")

def display_configuration():
    """Display current configuration"""
    if not st.session_state.pipeline_initialized:
        return
    
    st.subheader("⚙️ Configuration")
    
    try:
        status = st.session_state.pipeline.get_pipeline_status()
        config = status['config']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Text Processing:**")
            st.write(f"• Chunk Size: {config.get('chunk_size', 'N/A')} characters")
            st.write(f"• Chunk Overlap: {config.get('chunk_overlap', 'N/A')} characters")
        
        with col2:
            st.write("**Embedding Model:**")
            st.write(f"• Model: {config.get('embedding_model', 'N/A')}")
            st.write("**Supported Formats:**")
            formats = config.get('supported_formats', [])
            st.write(f"• {', '.join(formats)}")
        
    except Exception as e:
        st.error(f"Error loading configuration: {str(e)}")

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">⚖️ Legal Document Ingestion Pipeline</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Initialize pipeline if not already done
    if not st.session_state.pipeline_initialized:
        if not initialize_pipeline():
            st.stop()
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload & Process", "💾 Vector Store", "⚙️ Configuration", "🔍 Search"])

    with tab1:
        st.markdown("""
        <div class="status-box info-box">
            <h4>📖 How to Use</h4>
            <p>1. Upload one or more legal documents (PDF, DOCX, or TXT format)</p>
            <p>2. Click "Start Ingestion Process" to begin processing</p>
            <p>3. Monitor the progress and review results</p>
            <p>4. Documents will be stored in the vector database for RAG applications</p>
        </div>
        """, unsafe_allow_html=True)
        # File upload and processing
        uploaded_files = display_file_uploader()
        if uploaded_files:
            process_documents(uploaded_files)
        # Show last results if available
        if st.session_state.last_results:
            st.markdown("---")
            display_processing_results(st.session_state.last_results)

    with tab2:
        display_vector_store_status()

    with tab3:
        display_configuration()

    with tab4:
        st.subheader("🔍 Search for Related Chunks")
        st.markdown("Enter a search query to retrieve related document chunks using the same embedding model.")

        # Search bar
        search_query = st.text_input("Search Query", "", help="Type your question or keywords here")
        top_k = st.slider("Number of results", min_value=1, max_value=20, value=5)

        if st.button("🔎 Search", type="primary"):
            if not search_query.strip():
                st.warning("Please enter a search query.")
            else:
                with st.spinner("Generating embedding and searching..."):
                    try:
                        from src.embedding_generator import GeminiEmbeddingGenerator
                        from src.vector_store import FAISSVectorStore

                        embedder = GeminiEmbeddingGenerator()
                        vector_store = FAISSVectorStore()

                        query_embedding = embedder._get_single_embedding(search_query)
                        if query_embedding is None:
                            st.error("Failed to generate embedding for the search query.")
                        else:
                            results = vector_store.search(query_embedding, k=top_k)
                            if not results:
                                st.info("No related chunks found.")
                            else:
                                st.success(f"Found {len(results)} related chunks:")
                                for result in results:
                                    with st.expander(f"Rank {result['rank']} | Score: {result['similarity_score']:.4f}"):
                                        st.write(f"**Source Document:** {result.get('source_document', 'N/A')}")
                                        st.write(f"**File Type:** {result.get('file_type', 'N/A')}")
                                        st.write(f"**Chunk Text:**\n{result.get('text', '')}")
                                        st.write(f"**Characters:** {result.get('char_count', 0)}")
                    except Exception as e:
                        st.error(f"Search failed: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: #6b7280; font-size: 0.9rem;">'
        'Legal Document Ingestion Pipeline v1.0 | Built with Streamlit & Google Gemini'
        '</div>', 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
