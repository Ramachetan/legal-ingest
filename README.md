# Legal Document Ingestion Pipeline

A comprehensive Python-based ingestion pipeline for legal documents designed for Retrieval-Augmented Generation (RAG) applications. This application processes various document formats, generates embeddings using Google's Gemini Pro, and stores them in a FAISS vector database with an intuitive Streamlit interface.

## Features

- **Multi-format Support**: Handles PDF, DOCX, and TXT files
- **Intelligent Text Chunking**: Legal document-specific text splitting with semantic coherence
- **Google Gemini Integration**: Uses Gemini Pro for high-quality embeddings
- **Vector Storage**: FAISS-based vector database for efficient similarity search
- **Web Interface**: Interactive Streamlit UI for document upload and management
- **Progress Tracking**: Real-time processing status and detailed results
- **Metadata Management**: Comprehensive document and chunk metadata tracking

## Architecture

### 1. UI Layer (Streamlit)
- Interactive web interface for document upload
- Real-time processing status updates
- Vector store management and statistics
- Configuration display and management

### 2. Data Processing Layer
- **Document Loader**: Handles PDF, DOCX, TXT extraction
- **Text Splitter**: Legal document-optimized chunking
- **Embedding Generator**: Google Gemini Pro integration
- **Pipeline Orchestrator**: Coordinates the entire workflow

### 3. Storage Layer
- **FAISS Vector Store**: Efficient similarity search
- **Metadata Store**: JSON-based metadata persistence
- **Configuration Management**: Environment-based settings

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd legal-ingest
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   copy .env.example .env
   ```
   
   Edit `.env` and add your Google API key:
   ```
   GOOGLE_API_KEY=your_actual_google_api_key_here
   ```

## Usage

1. **Start the application**:
   ```bash
   streamlit run app.py
   ```

2. **Access the web interface**:
   - Open your browser to `http://localhost:8501`

3. **Upload documents**:
   - Use the file uploader to select PDF, DOCX, or TXT files
   - Monitor the processing progress
   - Review results and statistics

4. **Manage vector store**:
   - View stored documents and statistics
   - Clear data if needed
   - Monitor configuration settings

## Configuration

Key configuration options in `.env`:

```bash
# Google API Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Text Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_FILE_SIZE_MB=50

# Storage Paths
VECTOR_DB_PATH=./vector_store
FAISS_INDEX_PATH=./vector_store/faiss_index.index
METADATA_PATH=./vector_store/metadata.json

# Gemini Model Settings
EMBEDDING_MODEL=models/embedding-001
EMBEDDING_TASK_TYPE=retrieval_document
```

## Project Structure

```
legal-ingest/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
└── src/
    ├── config.py         # Configuration management
    ├── document_loader.py # Document text extraction
    ├── text_splitter.py  # Legal document chunking
    ├── embedding_generator.py # Gemini integration
    ├── vector_store.py   # FAISS vector database
    └── pipeline.py       # Main orchestrator
```

## Dependencies

- **streamlit**: Web interface framework
- **google-generativeai**: Google Gemini API client
- **PyPDF2**: PDF text extraction
- **python-docx**: DOCX document processing
- **faiss-cpu**: Vector similarity search
- **numpy**: Numerical computations
- **pandas**: Data manipulation
- **python-dotenv**: Environment variable management
- **tiktoken**: Token counting utilities

## API Key Setup

1. **Get a Google AI API Key**:
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create a new API key
   - Enable the Generative AI API

2. **Configure the key**:
   - Add to `.env` file: `GOOGLE_API_KEY=your_key_here`
   - Ensure the key has access to the `embedding-001` model

## Legal Document Processing Features

### Intelligent Text Chunking
- Hierarchical splitting prioritizing legal structure
- Preserves section boundaries and legal formatting
- Configurable chunk size and overlap
- Maintains semantic coherence

### Legal Section Recognition
- Identifies sections, articles, clauses, paragraphs
- Preserves legal document structure
- Enhanced metadata for better retrieval

### Document Format Support
- **PDF**: Multi-page extraction with page markers
- **DOCX**: Paragraph and table text extraction
- **TXT**: Multi-encoding support with fallback

## Vector Store Features

- **FAISS Integration**: Fast similarity search
- **Persistent Storage**: Index and metadata persistence
- **Metadata Tracking**: Comprehensive document information
- **Statistics**: Document counts, types, and dimensions
- **Management**: Clear data and status monitoring

## Error Handling

The pipeline includes comprehensive error handling:
- Document loading failures
- Text extraction errors
- Embedding generation retries
- Vector store persistence issues
- API rate limiting and connection errors

## Performance Considerations

- **Rate Limiting**: Built-in delays for API compliance
- **Memory Management**: Efficient chunk processing
- **Storage Optimization**: Compressed vector indices
- **Progress Tracking**: Real-time status updates

## Troubleshooting

### Common Issues

1. **API Key Not Working**:
   - Verify key in `.env` file
   - Check Google AI Studio access
   - Ensure embedding model permissions

2. **File Upload Errors**:
   - Check file size limits (50MB default)
   - Verify supported formats (PDF, DOCX, TXT)
   - Ensure files contain extractable text

3. **Memory Issues**:
   - Reduce chunk size in configuration
   - Process fewer documents simultaneously
   - Clear vector store if needed

4. **Import Errors**:
   - Verify all dependencies installed
   - Check Python version compatibility
   - Activate virtual environment

## Security Considerations

- Store API keys securely in environment variables
- Do not commit `.env` files to version control
- Consider file upload size limits
- Validate document content before processing

## Future Enhancements

- Support for additional document formats
- Advanced legal document parsing
- Query interface for stored documents
- Batch processing capabilities
- Advanced metadata filtering
- Integration with other embedding models

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the configuration settings
3. Verify API key and permissions
4. Create an issue with detailed error logs
