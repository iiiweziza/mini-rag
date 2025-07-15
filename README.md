# Mini-RAG Project

A comprehensive, modular Retrieval-Augmented Generation (RAG) backend for document upload, processing, chunking, and question answering, built with FastAPI, MongoDB, and LangChain.

---

## 🚀 Project Overview

Mini-RAG is a backend service for document-based Q&A and RAG workflows. It allows users to upload documents (PDF, TXT), processes and chunks them using LangChain, and stores all data in MongoDB. The project is designed for easy extension, robust data management, and rapid prototyping. It follows an MVC-like structure and is ready for research and production use.

---

## 🆕 What's New / Recent Updates
- Improved asset lookup: supports both ObjectId and string for MongoDB compatibility
- Enhanced error handling and validation for file uploads and processing
- Modularized controllers for easy extension (add new file types, chunking strategies, etc.)
- Dockerized MongoDB for local development
- More code comments and in-file documentation
- `.gitignore` best practices for uploaded files and database data

---

## 🗂️ Project Structure & File Roles

```
mini-rag/
├── docker/                 # Docker config for MongoDB
│   ├── docker-compose.yml  # MongoDB container setup
│   └── mongo-data/         # MongoDB data volume (ignored by git)
├── src/
│   ├── assets/             # Uploaded files, Postman collection
│   │   └── uploaded_files/ # Project-specific upload directories
│   ├── controllers/        # Business logic
│   │   ├── base_controller.py         # Common controller logic
│   │   ├── data_controller.py         # File validation, naming
│   │   ├── processing_controller.py   # File loading, chunking
│   │   └── project_controller.py      # Project directory management
│   ├── helpers/            # Config and settings
│   │   └── config.py
│   ├── models/             # DB models, enums, schemas
│   │   ├── enums/          # Enum types (file types, responses)
│   │   └── db_schemes/     # Pydantic schemas for DB
│   ├── routes/             # API endpoints
│   │   ├── base.py         # Welcome/info endpoints
│   │   └── data.py         # Upload and processing endpoints
│   ├── main.py             # FastAPI entry point
│   └── requirements.txt    # Python dependencies
├── .env.example            # Example environment variables
├── README.md               # Project documentation
└── ...
```

---

## ✨ Features
- Upload and validate files (PDF, TXT)
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

## 🔌 API Endpoints

### Base
- `GET /api/v1/` — Welcome/info

### Data
- `POST /api/v1/data/Upload/{Project_id}` — Upload a file to a project
- `POST /api/v1/data/process/{Project_id}` — Process all or a specific file in a project

#### Example Request (Upload)
```bash
curl -X POST "http://localhost:5000/api/v1/data/Upload/myproject" -F "file=@mydoc.pdf"
```

#### Example Request (Process)
```bash
curl -X POST "http://localhost:5000/api/v1/data/process/myproject" -H "Content-Type: application/json" -d '{"chunk_size": 500, "chunk_overlap": 50}'
```

---

## 🧩 Core Components Explained

- **Controllers**
  - `BaseController`: Common logic and config access
  - `DataController`: File validation, unique naming, cleaning
  - `ProcessingController`: Loads files, extracts content, chunks with LangChain
  - `ProjectController`: Manages project directories for uploads
- **Models**
  - `ProjectModel`: Project schema and DB operations
  - `AssetsFiles`: Asset/file schema
  - `DataChunk`: Chunk schema
  - `Enums`: Response codes, file types, DB collections
- **Routes**
  - `base.py`: Welcome/info endpoints
  - `data.py`: File upload and processing endpoints
- **Helpers**
  - `config.py`: Loads environment variables and settings

---

## 📝 Document Processing Flow

1. **Upload**: User uploads a file to a project via `/api/v1/data/Upload/{Project_id}`
2. **Validation**: File type and size are checked
3. **Storage**: File is saved in a project-specific directory
4. **Asset Record**: Metadata is stored in MongoDB
5. **Processing**: `/api/v1/data/process/{Project_id}` splits the file into chunks using LangChain
6. **Chunk Storage**: Chunks are stored in MongoDB for later retrieval

---

## 🛠️ Extending the Project

- **Add new file types**: Update `processingEnumType` and add loader logic in `ProcessingController`
- **Add new endpoints**: Create new route files in `src/routes/`
- **Change chunking logic**: Edit `process_file_content` in `ProcessingController`
- **Add authentication**: Extend FastAPI dependencies and middleware

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

## ❓ Troubleshooting

- If uploads are not ignored by git, ensure `docker/mongo-data/` is in your root `.gitignore`
- If MongoDB connection fails, check your `.env` and Docker status
- For CORS or API errors, check FastAPI logs and settings
- For asset lookup issues, ensure `asset_project_id` in MongoDB matches the project `_id` type (ObjectId or string)

---

## 📚 License

This project is licensed under the MIT License.

---

## 💬 Contact & Support

For questions, open an issue or contact the maintainers.





#####
for your envs 
conda env list