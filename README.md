# Mini-RAG Project

A FastAPI-based RAG (Retrieval-Augmented Generation) application for document processing and question answering.

## Project Overview

Mini-RAG is built with FastAPI and MongoDB, following an MVC-like architecture. It provides endpoints for file upload, document processing, and text chunking using LangChain.

### Key Features

- File upload with validation
- Document processing for PDF and TXT files
- Text chunking using LangChain's RecursiveCharacterTextSplitter
- MongoDB integration for data persistence
- Project-based organization of documents
- Configurable settings via environment variables

## Project Structure

```
mini-rag/
├── docker/                 # Docker configuration
│   ├── docker-compose.yml  # MongoDB container setup
│   └── mongo-data/        # MongoDB data volume
├── src/
│   ├── assets/            # Uploaded files and Postman collection
│   ├── controllers/       # Business logic
│   │   ├── base_controller.py
│   │   ├── data_controller.py
│   │   ├── processing_controller.py
│   │   └── project_controller.py
│   ├── helpers/          # Configuration utilities
│   │   └── config.py
│   ├── models/          # Database models and schemas
│   │   ├── enums/      # Enumeration types
│   │   └── db_schemes/ # Database schemas
│   ├── routes/         # API endpoints
│   │   ├── base.py    # Base routes
│   │   └── data.py    # Data handling routes
│   ├── .env.example   # Example environment variables
│   ├── main.py        # Application entry point
│   └── requirements.txt # Python dependencies
```

## Setup Instructions

1. **Clone the Repository**
```bash
git clone <repository-url>
cd mini-rag
```

2. **Set Up Python Environment**
```bash
conda create -n mini-rag python=3.8
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
```
Edit `.env` with your settings:
- APP_NAME
- APP_VERSION
- API_KEY
- FILE_ALLOWED_TYPE
- FILE_MAX_SIZE
- MONGO_URI
- MONGODB_DATA_BASE

5. **Start MongoDB**
```bash
cd docker
docker-compose up -d
```

6. **Run the Application**
```bash
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

## API Endpoints

### Base Route
- `GET /api/v1/` - Welcome endpoint

### Data Routes
- `POST /api/v1/data/Upload/{Project_id}` - Upload file to project
- `POST /api/v1/data/process/{Project_id}` - Process uploaded file

## Core Components

### Controllers
- **BaseController**: Common functionality and configuration
- **DataController**: File validation and handling
- **ProcessingController**: Document processing using LangChain
- **ProjectController**: Project management

### Models
- **Project**: Project schema and MongoDB operations
- **DataChunk**: Document chunk schema
- **Enums**: Response codes, file types, database collections

### Routes
- **base.py**: Application info endpoints
- **data.py**: File upload and processing endpoints

## Document Processing

Supports:
- Text files (.txt)
- PDF files (.pdf)
- Configurable chunk sizes and overlap
- LangChain text splitters for optimal chunking

## Technologies Used

- FastAPI
- MongoDB (with Motor async driver)
- LangChain
- PyMuPDF
- Docker (for MongoDB)
- Pydantic

## Development

1. **Adding New File Types**
   - Update `processingEnumType` in models/enums
   - Add loader in `ProcessingController`

2. **Extending Processing**
   - Modify `ProcessingController` for new processing methods
   - Update routes in `data.py`



   