# Mini-RAG Project

A sophisticated Retrieval-Augmented Generation (RAG) backend system built with FastAPI, MongoDB, Qdrant Vector Database, and LangChain. This project provides a robust infrastructure for document processing, semantic search, and AI-powered question answering.

## 🎯 Project Overview

Mini-RAG is a production-ready backend service that combines document processing with advanced NLP capabilities. It features:

- Document processing and chunking using LangChain
- Vector embeddings storage with Qdrant
- Document management with MongoDB
- REST API interface with FastAPI
- Project-based organization of documents and queries
- Modular architecture for easy extension

---

## 🆕 What's New / Recent Updates
- Integrated Qdrant vector database for efficient similarity search
- Improved NLP processing with advanced embedding support
- Enhanced error handling and validation for file uploads and processing
- Modularized controllers for easy extension (add new file types, chunking strategies, etc.)
- Added semantic search capabilities with configurable parameters
- Improved documentation and code comments

## 🏗️ Architecture

### Core Components

```
mini-rag/
├── docker/                     # Docker configurations
│   ├── docker-compose.yml     # MongoDB and Qdrant setup
│   └── mongo-data/            # Persistent MongoDB storage
├── src/
│   ├── assets/               # Project assets and uploads
│   │   ├── uploaded_files/   # Document storage
│   │   └── database/         # Database files
│   ├── controllers/          # Business logic layer
│   │   ├── base_controller.py       # Base controller functionality
│   │   ├── data_controller.py       # Data handling and validation
│   │   ├── nlp_controller.py        # NLP and vector operations
│   │   ├── processing_controller.py # Document processing
│   │   └── project_controller.py    # Project management
│   ├── helpers/             # Utilities and configurations
│   ├── models/              # Data models and schemas
│   │   ├── enums/          # Type definitions
│   │   └── db_schemes/     # Database schemas
│   ├── routes/             # API endpoints
│   │   ├── base.py        # Base routes
│   │   ├── data.py        # Data operations
│   │   └── nlp.py         # NLP operations
│   ├── stores/            # Storage interfaces
│   │   ├── llm/          # Language model interfaces
│   │   └── vector_db/    # Vector database client
│   └── main.py           # Application entry point
```

---

## ✨ Features
- Upload and validate files (PDF, TXT, CSV, Markdown, HTML, Excel)
- Upload and process URLs directly
- Project-based document organization
- Document chunking with LangChain (configurable size/overlap)
- MongoDB async storage for projects, assets, and chunks
- REST API for upload, processing, and retrieval
- Dockerized MongoDB for easy local development
- Extensible controllers for new file types and processing logic
- Environment-based configuration
- Postman collection for API testing

---

## ⚙️ Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd mini-rag
   ```
2. **Create Python Environment**
   ```bash
   conda create -n mini-rag python=3.12
   conda activate mini-rag
   ```
3. **Install Dependencies**
   ```bash
   pip install -r src/requirements.txt
   ```
4. **Configure Environment**
   ```bash
   cd src
   cp .env.example .env
   # Edit .env with your MongoDB URI, API keys, etc.
   ```
5. **Start MongoDB (Docker)**
   ```bash
   cd ../docker
   docker-compose up -d
   ```
6. **Run the Application**
   ```bash
   cd ../src
   uvicorn main:app --reload --host 0.0.0.0 --port 5000
   ```

---
# don't forget to install : 
  pip install "unstructured[all]" "unstructured-inference"
  pip install networkx pandas openpyxl xlrd
## 🔌 API Endpoints

### Base
- `GET /api/v1/` — Welcome/info

### Data Operations
- `POST /api/v1/data/Upload/{Project_id}` — Upload a file or URL to a project
- `POST /api/v1/data/process/{Project_id}` — Process all or a specific file in a project

### NLP Operations
- `POST /api/v1/nlp/index/push/{Project_id}` — Index documents into vector database
- `GET /api/v1/nlp/index/info/{Project_id}` — Get collection information
- `POST /api/v1/nlp/index/search/{Project_id}` — Semantic search in documents

#### Example Requests

**Upload Document:**
```bash
curl -X POST "http://localhost:5000/api/v1/data/Upload/myproject" -F "file=@mydoc.pdf"
```

**Upload URL:**
```bash
curl -X POST "http://localhost:5000/api/v1/data/Upload/myproject" \
  -F "url=https://example.com" \
  -F "chunk_size=100" \
  -F "chunk_overlap=20"
```

**Process Document:**
```bash
curl -X POST "http://localhost:5000/api/v1/data/process/myproject" \
  -H "Content-Type: application/json" \
  -d '{"chunk_size": 500, "chunk_overlap": 50}'
```

**Semantic Search:**
```bash
curl -X POST "http://localhost:5000/api/v1/nlp/index/search/myproject" \
  -H "Content-Type: application/json" \
  -d '{"text": "search query", "limit": 5}'
```

---

## 🧩 Core Components Explained

### Controllers
- **BaseController**
  - Common configuration and utility functions
  - Environment variable management
  - Base error handling

- **NLPController**
  - Vector database management
  - Embedding generation for documents and queries
  - Semantic search implementation
  - Collection management per project
  - Batch processing of document chunks

- **ProcessingController**
  - Document loading and text extraction
  - Support for PDF, TXT, CSV, Markdown, HTML, Excel formats
  - URL content processing and web scraping
  - LangChain integration for text splitting
  - Configurable chunking parameters

- **DataController**
  - File validation and sanitization
  - Unique file naming and organization
  - Asset tracking and metadata management

- **ProjectController**
  - Project lifecycle management
  - Directory structure organization
  - Resource allocation and cleanup

### Models
- **ProjectModel**
  - Project configuration and settings
  - MongoDB schema and operations
  - Project state management

- **Asset**
  - File metadata and storage information
  - Processing status tracking
  - File type validation

- **DataChunk**
  - Text chunk schema and metadata
  - Vector storage integration
  - Chunk processing state

### Stores
- **VectorDB**
  - Qdrant client implementation
  - Collection management
  - Vector operations and search

- **LLM**
  - Language model interfaces
  - Embedding generation
  - Model configuration

### Routes
- **base.py**
  - Application information
  - Health checks
  - Version details

- **data.py**
  - File upload endpoints
  - Processing triggers
  - Asset management

- **nlp.py**
  - Vector database operations
  - Semantic search endpoints
  - Collection management

---

## 📝 Document Processing Flow

### Unified Upload System
The system now supports both file uploads and URL processing through a single endpoint:

**File Upload:**
- Send file via `multipart/form-data` with `file` field
- Supports: PDF, TXT, CSV, Markdown, HTML, Excel
- File is saved locally and metadata stored in MongoDB

**URL Upload:**
- Send form data with `url`, `chunk_size`, and `chunk_overlap` fields
- URL content is downloaded, processed, and chunked immediately
- Chunks are stored directly in MongoDB (no local file storage)

1. **Document Upload**
   - User uploads file or URL via `/api/v1/data/Upload/{Project_id}`
   - Automatic detection of upload type (file vs URL)
   - Validation and type checking
   - Storage in project-specific directory (files) or direct processing (URLs)
   - Metadata registration in MongoDB

2. **Text Processing**
   - Document loading with appropriate handler (PDF/TXT)
   - Text extraction and cleaning
   - Chunking with LangChain
   - Metadata enrichment

3. **Vector Processing**
   - Embedding generation for each chunk
   - Vector quality validation
   - Batch insertion into Qdrant
   - Collection management and optimization

4. **Search Preparation**
   - Collection indexing
   - Metadata linking
   - Search configuration
   - Performance optimization

## 🛠️ Extending the Project

### Adding New Document Types
1. Update `processingEnumType` enum
2. Implement loader in `ProcessingController`
3. Add validation in `DataController`
4. Update processing pipeline

### Customizing Vector Search
1. Modify `NLPController` search parameters
2. Adjust vector collection settings
3. Implement custom ranking logic
4. Add new search endpoints

### Enhancing Processing
1. Customize chunking in `ProcessingController`
2. Add new processing strategies
3. Implement custom metadata extraction
4. Extend the processing pipeline

### Adding Authentication
1. Implement FastAPI security dependencies
2. Add JWT or OAuth2 support
3. Create user management system
4. Set up role-based access control

---

## 🐳 Docker & Data

- MongoDB runs in Docker for easy setup
- All data in `docker/mongo-data/` is ignored by git (add `docker/mongo-data/` to your root `.gitignore`)

---

## 🧑‍💻 Development & Contribution

- Use conda or venv for Python environment
- All config is in `.env` (see `.env.example`)
- Use the included Postman collection for API testing (`src/assets/mini-rag-app.postman_collection.json`)
- Code is modular and ready for extension
- See `PROJECT_DOCUMENTATION.txt` for more technical details

---

## ⚡ Performance Optimization

### Vector Search
- Use appropriate index settings in Qdrant
- Optimize chunk sizes for your use case
- Configure proper vector dimensions
- Use batch operations for insertions

### Document Processing
- Implement parallel processing for large files
- Use appropriate chunk overlap
- Optimize text cleaning procedures
- Cache frequently accessed data

### Database Operations
- Index frequently queried fields
- Use bulk operations when possible
- Implement connection pooling
- Monitor query performance

## ❓ Troubleshooting

### Vector Database Issues
- Verify Qdrant connection settings
- Check collection creation logs
- Validate vector dimensions
- Monitor indexing performance

### Document Processing Issues
- Verify file permissions
- Check supported formats
- Monitor chunking logs
- Validate processing output

### MongoDB Issues
- Check connection string in `.env`
- Verify Docker container status
- Monitor disk space usage
- Check collection indexes

### API Issues
- Monitor FastAPI logs
- Check CORS settings
- Verify endpoint configurations
- Test with Postman collection

## 📚 Resources & Links

- [Project Documentation](./PROJECT_DOCUMENTATION.txt)
- [Qdrant Documentation](https://qdrant.tech/documentation/overview/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [MongoDB Documentation](https://www.mongodb.com/docs/)

## � License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## 💬 Support & Contact

For support:
1. Check the documentation
2. Search existing issues
3. Open a new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details