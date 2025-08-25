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

# Set wide layout
st.set_page_config(
    page_title="Legal Document Ingestion Pipeline",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    /* Main layout improvements */
    .main > div {
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 95%;
    }
    
    .main-header {
        font-size: 3rem;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 1.5rem;
        padding: 1rem 0;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 1rem;
        border: 1px solid #cbd5e1;
    }
    
    .subheader {
        font-size: 1.5rem;
        color: #374151;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e5e7eb;
    }
    
    .status-box {
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    
    .success-box {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border: 2px solid #10b981;
        color: #065f46;
    }
    
    .error-box {
        background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%);
        border: 2px solid #ef4444;
        color: #991b1b;
    }
    
    .info-box {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border: 2px solid #3b82f6;
        color: #1e40af;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 2px solid #f59e0b;
        color: #92400e;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border: 2px solid #e2e8f0;
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    }
    
    .metric-card h3 {
        font-size: 2.5rem;
        color: #1e40af;
        margin: 0;
        font-weight: bold;
    }
    
    .metric-card p {
        color: #64748b;
        margin: 0.5rem 0 0 0;
        font-weight: 500;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f1f5f9;
        padding: 0.5rem;
        border-radius: 0.75rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        border-radius: 0.5rem;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 0.75rem;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* File uploader styling */
    .uploadedFile {
        border: 2px dashed #cbd5e1;
        border-radius: 1rem;
        padding: 2rem;
        margin: 1rem 0;
        background: #f8fafc;
        transition: border-color 0.2s;
    }
    
    .uploadedFile:hover {
        border-color: #3b82f6;
        background: #f0f9ff;
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        border-radius: 0.5rem;
        height: 1rem;
    }
    
    /* Search input styling */
    .stTextInput > div > div > input {
        border-radius: 0.75rem;
        border: 2px solid #e2e8f0;
        padding: 0.75rem 1rem;
        font-size: 1.1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        border-radius: 0.5rem;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Remove extra padding */
    .element-container {
        margin-bottom: 1rem !important;
    }
    
    /* Custom separator */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #cbd5e1, transparent);
        margin: 2rem 0;
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
    """Display enhanced file upload interface"""    
    # Create columns for better layout
    upload_col1, upload_col2 = st.columns([2, 1])
    
    with upload_col1:
        uploaded_files = st.file_uploader(
            "",  # Empty label since we'll add custom header
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=True,
            help="Drag and drop files here or click to browse. Maximum file size: 50MB per file.",
            label_visibility="collapsed"
        )
    
    with upload_col2:
        st.markdown("""
        <div style="background: #f0f9ff; padding: 1rem; border-radius: 0.75rem; border: 2px dashed #3b82f6; text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📁</div>
            <div style="color: #1e40af; font-weight: 600;">Supported Formats</div>
            <div style="color: #3b82f6; font-size: 0.9rem; margin-top: 0.5rem;">
                PDF • DOCX • TXT<br>
                <small>Max: 50MB each</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if uploaded_files:
        st.markdown("---")
        
        # File preview section
        st.markdown("""
        <div style="background: #f8fafc; padding: 1rem; border-radius: 0.75rem; border: 1px solid #e2e8f0; margin: 1rem 0;">
            <h4 style="color: #374151; margin-bottom: 1rem;">📋 Selected Files Preview</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Display files in a grid layout
        total_size = 0
        file_details = []
        
        for i, file in enumerate(uploaded_files):
            file_size = len(file.getvalue()) / (1024 * 1024)  # Convert to MB
            total_size += file_size
            
            # Determine file type icon
            file_ext = file.name.split('.')[-1].lower()
            if file_ext == 'pdf':
                icon = "📄"
                type_color = "#dc2626"
            elif file_ext == 'docx':
                icon = "📝"
                type_color = "#2563eb"
            else:
                icon = "📃"
                type_color = "#059669"
            
            file_details.append({
                'name': file.name,
                'size': file_size,
                'icon': icon,
                'color': type_color,
                'type': file_ext.upper()
            })
        
        # Display files in columns
        cols = st.columns(min(len(file_details), 3))
        for i, details in enumerate(file_details):
            col_index = i % len(cols)
            with cols[col_index]:
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 0.5rem; border: 1px solid #e5e7eb; margin-bottom: 0.5rem; text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">{details['icon']}</div>
                    <div style="font-weight: 600; color: #374151; font-size: 0.9rem; margin-bottom: 0.25rem;">
                        {details['name'][:25]}{'...' if len(details['name']) > 25 else ''}
                    </div>
                    <div style="color: {details['color']}; font-weight: 500; font-size: 0.8rem; margin-bottom: 0.25rem;">
                        {details['type']}
                    </div>
                    <div style="color: #6b7280; font-size: 0.8rem;">
                        {details['size']:.1f} MB
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Summary information
        st.markdown(f"""
        <div style="background: #ecfdf5; padding: 1rem; border-radius: 0.75rem; border: 1px solid #10b981; margin: 1rem 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="color: #065f46;">📊 Upload Summary</strong>
                    <div style="color: #047857; font-size: 0.9rem;">
                        {len(uploaded_files)} file(s) • {total_size:.1f} MB total
                    </div>
                </div>
                <div style="color: #059669; font-size: 1.5rem;">
                    ✅
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        # Empty state with better guidance
        st.markdown("""
        <div style="text-align: center; padding: 3rem 1rem; border: 2px dashed #cbd5e1; border-radius: 1rem; background: #f8fafc; margin: 1rem 0;">
            <div style="font-size: 3rem; color: #94a3b8; margin-bottom: 1rem;">📁</div>
            <div style="color: #475569; font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">
                No files selected
            </div>
            <div style="color: #64748b; font-size: 1rem;">
                Upload your legal documents to get started with processing
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    return uploaded_files

def process_documents(uploaded_files):
    """Process uploaded documents through the pipeline with enhanced UI feedback"""
    if not uploaded_files:
        st.warning("⚠️ Please select files to process.")
        return
    
    if st.session_state.processing:
        st.markdown("""
        <div class="status-box warning-box">
            <h4>⏳ Processing in Progress</h4>
            <p>Please wait while the current batch is being processed. This may take a few minutes depending on file size and content.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Enhanced processing button
    button_col1, button_col2, button_col3 = st.columns([1, 2, 1])
    with button_col2:
        start_processing = st.button(
            "🚀 Start Document Processing", 
            type="primary", 
            disabled=st.session_state.processing,
            use_container_width=True,
            help="Begin processing all uploaded documents through the ingestion pipeline"
        )
    
    if start_processing:
        st.session_state.processing = True
        
        # Processing overview
        st.markdown(f"""
        <div class="status-box info-box">
            <h4>🔄 Processing Started</h4>
            <p>Processing {len(uploaded_files)} document(s) through the ingestion pipeline:</p>
            <div style="margin-top: 0.5rem;">
                {''.join([f"<span style='margin-right: 0.5rem;'>📄 {file.name}</span>" for file in uploaded_files])}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Prepare file data
        file_data = []
        for file in uploaded_files:
            file_data.append({
                'name': file.name,
                'data': file.getvalue()
            })
        
        # Create enhanced progress display
        progress_container = st.container()
        with progress_container:
            st.markdown("### 📊 Processing Progress")
            
            # Progress elements
            overall_progress = st.progress(0, text="Initializing...")
            current_step = st.empty()
            step_details = st.empty()
            
            # Processing stats
            stats_col1, stats_col2, stats_col3 = st.columns(3)
            with stats_col1:
                processed_files = st.empty()
            with stats_col2:
                current_chunks = st.empty()
            with stats_col3:
                current_embeddings = st.empty()
        
        def enhanced_progress_callback(message, percentage):
            """Enhanced progress callback with better visual feedback"""
            # Update progress bar
            overall_progress.progress(int(percentage), text=f"Processing... {int(percentage)}%")
            
            # Update current step
            current_step.markdown(f"""
            <div style="background: #f0f9ff; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #3b82f6; margin: 0.5rem 0;">
                <div style="color: #1e40af; font-weight: 600;">🔄 {message}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Update step details based on message content
            if "Loading" in message:
                step_details.markdown("📥 **Loading and parsing document content...**")
            elif "Splitting" in message:
                step_details.markdown("✂️ **Breaking text into semantic chunks...**")
            elif "Embedding" in message:
                step_details.markdown("🧠 **Generating vector embeddings using Gemini...**")
            elif "Storing" in message:
                step_details.markdown("💾 **Saving to vector database...**")
        
        try:
            # Start processing with enhanced feedback
            with st.spinner("🔄 Initializing processing pipeline..."):
                time.sleep(0.5)  # Brief pause for UX
                results = st.session_state.pipeline.ingest_documents(
                    file_data, 
                    progress_callback=enhanced_progress_callback
                )
            
            # Processing complete
            overall_progress.progress(100, text="✅ Processing Complete!")
            current_step.markdown("""
            <div style="background: #f0fdf4; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #22c55e; margin: 0.5rem 0;">
                <div style="color: #15803d; font-weight: 600;">✅ All documents processed successfully!</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.session_state.last_results = results
            st.session_state.processing = False
            
            # Success celebration
            st.balloons()
            
            # Display results
            st.markdown("---")
            display_processing_results(results)
            
            # Post-processing actions
            if results['success']:
                st.markdown("""
                <div class="status-box success-box">
                    <h4>🎉 What's Next?</h4>
                    <p>Your documents are now ready! You can:</p>
                    <p>• <strong>Search</strong> through your documents using the Search tab</p>
                    <p>• <strong>View</strong> database statistics in the Vector Database tab</p>
                    <p>• <strong>Upload</strong> more documents to expand your knowledge base</p>
                </div>
                """, unsafe_allow_html=True)
            
        except Exception as e:
            st.session_state.processing = False
            
            # Error handling with better UX
            overall_progress.progress(0, text="❌ Processing failed")
            current_step.markdown(f"""
            <div style="background: #fef2f2; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #ef4444; margin: 0.5rem 0;">
                <div style="color: #dc2626; font-weight: 600;">❌ Processing Error</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="status-box error-box">
                <h4>❌ Processing Failed</h4>
                <p><strong>Error:</strong> {str(e)}</p>
                <div style="margin-top: 1rem;">
                    <strong>Troubleshooting suggestions:</strong>
                    <ul style="margin-top: 0.5rem;">
                        <li>Check your internet connection</li>
                        <li>Verify that your Google API key is valid</li>
                        <li>Ensure files are not corrupted or password-protected</li>
                        <li>Try processing fewer files at once</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)

def display_processing_results(results: Dict[str, Any]):
    """Display enhanced results of document processing"""
    st.markdown('<div class="subheader">📊 Processing Results</div>', unsafe_allow_html=True)
    
    # Main success/error status
    if results['success']:
        st.markdown(f"""
        <div class="status-box success-box">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <h3 style="margin: 0; color: #065f46;">🎉 Processing Complete!</h3>
                    <p style="margin: 0.5rem 0 0 0;">All {len(results['processed_documents'])} documents have been successfully processed and stored in the vector database.</p>
                </div>
                <div style="font-size: 3rem; opacity: 0.7;">✅</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="status-box error-box">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <h3 style="margin: 0; color: #991b1b;">⚠️ Partial Processing Complete</h3>
                    <p style="margin: 0.5rem 0 0 0;">
                        <strong>{len(results['processed_documents'])} succeeded</strong> • 
                        <strong>{len(results['failed_documents'])} failed</strong>
                    </p>
                </div>
                <div style="font-size: 3rem; opacity: 0.7;">⚠️</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced metrics grid
    st.markdown("### 📈 Processing Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #059669; font-size: 2rem; margin-bottom: 0.5rem;">📄</div>
            <h3 style="color: #059669;">{len(results['processed_documents'])}</h3>
            <p>Documents Processed</p>
            <div style="width: 100%; background: #e5e7eb; border-radius: 0.25rem; height: 0.5rem; margin-top: 0.5rem;">
                <div style="width: {(len(results['processed_documents']) / (len(results['processed_documents']) + len(results['failed_documents']))) * 100 if (len(results['processed_documents']) + len(results['failed_documents'])) > 0 else 0}%; background: #10b981; border-radius: 0.25rem; height: 100%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        failure_color = "#ef4444" if len(results['failed_documents']) > 0 else "#94a3b8"
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: {failure_color}; font-size: 2rem; margin-bottom: 0.5rem;">❌</div>
            <h3 style="color: {failure_color};">{len(results['failed_documents'])}</h3>
            <p>Documents Failed</p>
            <div style="width: 100%; background: #e5e7eb; border-radius: 0.25rem; height: 0.5rem; margin-top: 0.5rem;">
                <div style="width: {(len(results['failed_documents']) / (len(results['processed_documents']) + len(results['failed_documents']))) * 100 if (len(results['processed_documents']) + len(results['failed_documents'])) > 0 else 0}%; background: #ef4444; border-radius: 0.25rem; height: 100%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #3b82f6; font-size: 2rem; margin-bottom: 0.5rem;">📝</div>
            <h3 style="color: #3b82f6;">{results['total_chunks']}</h3>
            <p>Text Chunks Generated</p>
            <div style="color: #6b7280; font-size: 0.8rem; margin-top: 0.25rem;">
                Avg: {results['total_chunks'] // max(len(results['processed_documents']), 1)} per doc
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #8b5cf6; font-size: 2rem; margin-bottom: 0.5rem;">🧠</div>
            <h3 style="color: #8b5cf6;">{results['total_embeddings']}</h3>
            <p>Vector Embeddings</p>
            <div style="color: #6b7280; font-size: 0.8rem; margin-top: 0.25rem;">
                Ready for search
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Detailed results with enhanced presentation
    if results['processed_documents']:
        st.markdown("### ✅ Successfully Processed Documents")
        
        for i, doc in enumerate(results['processed_documents'], 1):
            with st.expander(f"📄 **{doc['filename']}** - {doc['chunk_count']} chunks created"):
                doc_col1, doc_col2, doc_col3 = st.columns([2, 1, 1])
                
                with doc_col1:
                    st.markdown("**📊 Processing Details:**")
                    st.write(f"• **File Type:** {doc.get('file_type', 'Unknown').upper()}")
                    st.write(f"• **File Size:** {doc.get('file_size', 'Unknown')}")
                    st.write(f"• **Processing Time:** {doc.get('processing_time', 'Unknown')}")
                
                with doc_col2:
                    st.markdown("**📝 Text Analysis:**")
                    st.metric("Chunks Created", doc['chunk_count'])
                    st.write(f"**Avg Chunk Size:** {doc.get('avg_chunk_size', 'N/A')} chars")
                
                with doc_col3:
                    st.markdown("**🧠 Embeddings:**")
                    st.metric("Vectors Generated", doc['embedding_count'])
                    st.write(f"**Vector Dimension:** {doc.get('vector_dimension', 'N/A')}")
                
                # Processing status bar
                st.markdown(f"""
                <div style="margin-top: 1rem; padding: 0.75rem; background: #f0fdf4; border-radius: 0.5rem; border: 1px solid #22c55e;">
                    <div style="display: flex; align-items: center;">
                        <div style="color: #16a34a; margin-right: 0.5rem;">✅</div>
                        <div style="color: #15803d; font-weight: 600;">Successfully ingested and ready for search</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    if results['failed_documents']:
        st.markdown("### ❌ Failed Documents")
        st.markdown("""
        <div class="status-box warning-box">
            <h4>⚠️ Processing Issues Detected</h4>
            <p>The following documents encountered errors during processing. Please check the details below and consider re-uploading or reformatting these files.</p>
        </div>
        """, unsafe_allow_html=True)
        
        for i, doc in enumerate(results['failed_documents'], 1):
            with st.expander(f"⚠️ **{doc['filename']}** - Processing failed"):
                st.markdown("**🔍 Error Analysis:**")
                
                error_col1, error_col2 = st.columns([2, 1])
                
                with error_col1:
                    st.markdown("**Error Details:**")
                    for j, error in enumerate(doc['errors'], 1):
                        st.markdown(f"**{j}.** {error}")
                
                with error_col2:
                    st.markdown("**Troubleshooting:**")
                    st.markdown("""
                    • Check file format
                    • Verify file isn't corrupted
                    • Ensure file isn't password protected
                    • Try converting to a different format
                    """)
                
                # Retry suggestion
                st.markdown(f"""
                <div style="margin-top: 1rem; padding: 0.75rem; background: #fef3c7; border-radius: 0.5rem; border: 1px solid #f59e0b;">
                    <div style="display: flex; align-items: center;">
                        <div style="color: #d97706; margin-right: 0.5rem;">💡</div>
                        <div style="color: #92400e; font-weight: 500;">Consider re-uploading this file after checking the format and content</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

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

def display_sidebar():
    """Display sidebar with helpful information and quick stats"""
    with st.sidebar:
        st.markdown("### 🚀 Quick Start")
        st.markdown("""
        1. **Upload** your legal documents
        2. **Process** through the pipeline
        3. **Search** using natural language
        4. **Export** or integrate results
        """)
        
        st.markdown("---")
        
        # Quick stats if pipeline is initialized
        if st.session_state.pipeline_initialized:
            try:
                status = st.session_state.pipeline.get_pipeline_status()
                stats = status['vector_store_stats']
                
                st.markdown("### 📊 Quick Stats")
                st.metric("Documents", stats.get('unique_documents', 0))
                st.metric("Text Chunks", stats.get('total_vectors', 0))
                st.metric("Vector Size", f"{stats.get('dimension', 0)}D")
                
            except:
                pass
        
        st.markdown("---")
        
        st.markdown("### 📋 Supported Formats")
        st.markdown("""
        - **PDF** - Adobe PDF documents
        - **DOCX** - Microsoft Word documents  
        - **TXT** - Plain text files
        """)
        
        st.markdown("---")
        
        st.markdown("### ⚡ Features")
        st.markdown("""
        - **Smart Text Splitting** - Intelligent chunking
        - **Embedding Generation** - Google Gemini API
        - **Vector Search** - FAISS similarity search
        - **Batch Processing** - Multiple file support
        - **Progress Tracking** - Real-time updates
        """)
        
        st.markdown("---")
        
        # System status indicator
        if st.session_state.pipeline_initialized:
            st.success("🟢 System Ready")
        else:
            st.error("🔴 System Initializing")
            
        if st.session_state.processing:
            st.warning("🟡 Processing...")

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Display sidebar
    display_sidebar()
    
    # Main content area
    col1, col2, col3 = st.columns([1, 10, 1])  # Create wider center column
    
    with col2:
        # Header with better styling
        st.markdown('''
        <div class="main-header">
            ⚖️ Legal Document Ingestion Pipeline
            <div style="font-size: 1.2rem; font-weight: normal; margin-top: 0.5rem; color: #64748b;">
                Intelligent document processing for legal research and RAG applications
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Initialize pipeline if not already done
        if not st.session_state.pipeline_initialized:
            st.markdown("""
            <div class="status-box warning-box">
                <h4>🔧 Initializing System</h4>
                <p>Please wait while we set up the document processing pipeline...</p>
            </div>
            """, unsafe_allow_html=True)
            
            if not initialize_pipeline():
                st.stop()
        
        # Main tabs with improved layout
        tab1, tab2, tab3, tab4 = st.tabs([
            "📤 Upload & Process", 
            "💾 Vector Database", 
            "🔍 Search & Query", 
            "⚙️ Settings"
        ])

        with tab1:
            # Welcome message with better styling
            st.markdown("""
            <div class="status-box info-box">
                <h4>📖 Document Processing Workflow</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">
                    <div style="text-align: center; padding: 1rem;">
                        <div style="font-size: 2rem;">📄</div>
                        <strong>1. Upload</strong><br>
                        <small>Select your legal documents</small>
                    </div>
                    <div style="text-align: center; padding: 1rem;">
                        <div style="font-size: 2rem;">⚙️</div>
                        <strong>2. Process</strong><br>
                        <small>Intelligent text splitting</small>
                    </div>
                    <div style="text-align: center; padding: 1rem;">
                        <div style="font-size: 2rem;">🧠</div>
                        <strong>3. Embed</strong><br>
                        <small>Generate semantic vectors</small>
                    </div>
                    <div style="text-align: center; padding: 1rem;">
                        <div style="font-size: 2rem;">💾</div>
                        <strong>4. Store</strong><br>
                        <small>Save to vector database</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # File upload section with better spacing
            st.markdown('<div class="subheader">📤 Document Upload</div>', unsafe_allow_html=True)
            
            uploaded_files = display_file_uploader()
            
            if uploaded_files:
                st.markdown("---")
                process_documents(uploaded_files)
            
            # Show last results if available
            if st.session_state.last_results:
                st.markdown("---")
                display_processing_results(st.session_state.last_results)

        with tab2:
            st.markdown('<div class="subheader">💾 Vector Database Management</div>', unsafe_allow_html=True)
            display_vector_store_status()

        with tab3:
            st.markdown('<div class="subheader">🔍 Semantic Search Interface</div>', unsafe_allow_html=True)
            
            # Enhanced search interface
            st.markdown("""
            <div class="status-box info-box">
                <h4>💡 Search Tips</h4>
                <p>• Use natural language queries for best results</p>
                <p>• Try legal terminology and concepts</p>
                <p>• Search results are ranked by semantic similarity</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Search interface with better layout
            col_search1, col_search2 = st.columns([3, 1])
            
            with col_search1:
                search_query = st.text_input(
                    "🔍 Enter your search query", 
                    placeholder="e.g., 'contract liability clauses' or 'employment termination procedures'",
                    help="Type your question or keywords here"
                )
            
            with col_search2:
                top_k = st.selectbox(
                    "Results to show", 
                    options=[3, 5, 10, 15, 20], 
                    index=1,
                    help="Number of most similar chunks to retrieve"
                )

            # Search button with better styling
            search_col1, search_col2, search_col3 = st.columns([1, 2, 1])
            with search_col2:
                search_clicked = st.button("🔎 Search Documents", type="primary", use_container_width=True)

            if search_clicked:
                if not search_query.strip():
                    st.warning("⚠️ Please enter a search query to continue.")
                else:
                    with st.spinner("🧠 Generating embeddings and searching..."):
                        try:
                            from src.embedding_generator import GeminiEmbeddingGenerator
                            from src.vector_store import FAISSVectorStore

                            embedder = GeminiEmbeddingGenerator()
                            vector_store = FAISSVectorStore()

                            query_embedding = embedder._get_single_embedding(search_query)
                            if query_embedding is None:
                                st.error("❌ Failed to generate embedding for the search query.")
                            else:
                                results = vector_store.search(query_embedding, k=top_k)
                                if not results:
                                    st.markdown("""
                                    <div class="status-box warning-box">
                                        <h4>🔍 No Results Found</h4>
                                        <p>No related chunks found for your query. Try:</p>
                                        <p>• Using different keywords or phrases</p>
                                        <p>• Checking if documents have been processed</p>
                                        <p>• Adding more documents to the database</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown(f"""
                                    <div class="status-box success-box">
                                        <h4>✅ Found {len(results)} Related Chunks</h4>
                                        <p>Results ranked by semantic similarity to your query: "<strong>{search_query}</strong>"</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    for i, result in enumerate(results, 1):
                                        similarity_color = "🟢" if result['similarity_score'] > 0.8 else "🟡" if result['similarity_score'] > 0.6 else "🔴"
                                        
                                        with st.expander(
                                            f"{similarity_color} **Result {i}** | Similarity: {result['similarity_score']:.3f} | Source: {result.get('source_document', 'Unknown')}"
                                        ):
                                            col_res1, col_res2 = st.columns([2, 1])
                                            
                                            with col_res1:
                                                st.markdown("**📄 Document Chunk:**")
                                                st.text_area(
                                                    "Content", 
                                                    value=result.get('text', ''), 
                                                    height=200, 
                                                    key=f"result_text_{i}",
                                                    disabled=True
                                                )
                                            
                                            with col_res2:
                                                st.markdown("**📊 Metadata:**")
                                                st.write(f"**File:** {result.get('source_document', 'N/A')}")
                                                st.write(f"**Type:** {result.get('file_type', 'N/A').upper()}")
                                                st.write(f"**Size:** {result.get('char_count', 0)} chars")
                                                st.write(f"**Rank:** #{result['rank']}")
                                                
                                                # Copy button for the text
                                                st.button(
                                                    "📋 Copy Text", 
                                                    key=f"copy_btn_{i}",
                                                    help="Copy chunk text to clipboard"
                                                )
                                                
                        except Exception as e:
                            st.error(f"❌ Search failed: {str(e)}")

        with tab4:
            st.markdown('<div class="subheader">⚙️ System Configuration</div>', unsafe_allow_html=True)
            display_configuration()
        
        # Footer with better styling
        st.markdown("---")
        st.markdown(
            '''
            <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); border-radius: 1rem; margin-top: 2rem;">
                <div style="color: #475569; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">
                    ⚖️ Legal Document Ingestion Pipeline v1.0
                </div>
                <div style="color: #64748b; font-size: 0.9rem;">
                    Powered by Streamlit • Google Gemini • FAISS Vector Search
                </div>
                <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 0.5rem;">
                    Built for legal research and document analysis workflows
                </div>
            </div>
            ''', 
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()
