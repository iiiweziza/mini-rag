# Lyzda: Production-Ready Retrieval-Augmented Generation Platform

This is a production-ready implementation of the RAG (Retrieval-Augmented Generation) model for enterprise question answering and document processing. It provides a complete system for ingesting documents, indexing them into a vector database, and performing intelligent question-answering queries using state-of-the-art LLMs.

## Project Overview

Lyzda is designed as a scalable, production-grade platform that enables organizations to leverage their document repositories for intelligent search and question answering. Built with enterprise requirements in mind, it offers robust security, high performance, and seamless integration capabilities.

The platform supports multiple data sources including local document uploads and web content crawling, processes documents into searchable chunks, indexes them in vector databases, and provides powerful natural language querying capabilities. With support for multiple LLM providers and vector databases, it offers flexibility to adapt to various infrastructure requirements.

## Production Features

### Enterprise Security
- JWT-based authentication with RSA key pairs
- Secure password hashing using industry-standard algorithms
- Role-based access control (user/admin permissions)
- Encrypted communication and secure key management

### Scalability & Performance
- Asynchronous processing for high throughput
- Batch operations for efficient data handling
- Connection pooling for database optimization
- Horizontal scaling capabilities

### Multi-Provider Support
- Multiple LLM providers (OpenAI, Cohere)
- Multiple vector database backends (Qdrant, PGVector)
- Flexible configuration for different deployment environments

### Data Management
- Comprehensive document processing pipeline
- Web crawling and content extraction
- Intelligent text chunking for optimal retrieval
- Full metadata preservation and management

### Observability & Monitoring
- Structured logging for monitoring and debugging
- Health check endpoints
- Performance metrics collection ready

## Architecture

The application follows a modular microservices-inspired architecture with clear separation of concerns:

- **Routes**: Handle HTTP requests and responses with proper validation
- **Controllers**: Implement business logic with transaction safety
- **Models**: Manage data structures and database interactions
- **Stores**: Provide interfaces to external services (LLMs, Vector Databases)
- **Helpers**: Utility functions and configuration management

## Directory Structure

```
src/
├── assets/                 # Static assets and security keys
├── controllers/            # Business logic implementation
├── helpers/                # Configuration and utility functions
├── models/                 # Data models and database schemes
├── routes/                 # API endpoint definitions
├── stores/                 # External service integrations (LLM, VectorDB)
└── main.py                 # Application entry point
```

## Core Components

### Main Application (`main.py`)

The main entry point initializes the FastAPI application and sets up all required services:
- Database connection using SQLAlchemy
- LLM provider factory for text generation and embeddings
- Vector database client for similarity search
- Template parser for internationalization
- Startup and shutdown event handlers

### Routes

#### Base Route (`routes/base.py`)
- Provides basic health check endpoint at `/api/v1/`
- Returns application name and version

#### User Route (`routes/user.py`)
- User registration and authentication
- JWT token generation (access and refresh tokens)
- Password hashing and verification
- RSA key-based token signing

#### Data Route (`routes/data.py`)
- File upload handling for various document types
- Web crawling capabilities for processing URLs
- Document validation and storage
- File chunking and preprocessing

#### NLP Route (`routes/nlp.py`)
- Vector indexing of processed documents
- Semantic search capabilities
- Question answering using RAG approach

### Controllers

#### BaseController (`controllers/BaseController.py`)
- Base class for all controllers providing common functionality

#### DataController (`controllers/DataController.py`)
- Validates uploaded files against allowed types and size limits
- Generates unique file paths for storage

#### NLPController (`controllers/NLPController.py`)
- Orchestrates the RAG pipeline
- Handles embedding generation and vector database operations
- Processes search queries and generates responses

#### ProcessController (`controllers/ProcessController.py`)
- Manages document loading from various sources
- Text extraction and chunking operations
- Web crawling functionality

#### ProjectController (`controllers/ProjectController.py`)
- Project-level operations and management
- File path generation for project-specific storage

#### UserController (`controllers/UserController.py`)
- User management operations
- Password handling and verification

### Models

#### Database Schemes (`models/db_schemes/`)
- **User**: User account information with secure password hashing
- **Project**: Project containers for organizing documents
- **Asset**: Uploaded files and their metadata
- **DataChunk**: Processed document chunks with embeddings

#### Data Models (`models/`)
- **AssetModel**: Operations on asset records
- **ChunkModel**: Management of document chunks
- **ProjectModel**: Project-level data operations
- **UserModel**: User data access and manipulation

### Stores

#### LLM Store (`stores/llm/`)
Supports multiple LLM providers:
- **OpenAIProvider**: Integration with OpenAI GPT models
- **CohereProvider**: Integration with Cohere AI models

Features:
- Text generation capabilities
- Embedding generation for vector search
- Template-based prompt engineering
- Multi-language support

#### VectorDB Store (`stores/vectordb/`)
Supports multiple vector database backends:
- **QdrantDBProvider**: Integration with Qdrant vector database
- **PGVectorProvider**: Integration with PostgreSQL-based PGVector

Features:
- Collection management
- Vector insertion and similarity search
- Batch operations for efficient indexing

## Key Features

### Document Processing
- Support for multiple file formats
- Web page crawling and processing
- Intelligent text chunking for optimal retrieval
- Metadata preservation

### Security
- JWT-based authentication with RSA keys
- Secure password hashing using PBKDF2
- Input validation and sanitization
- Role-based access control (user/superuser)

### Scalability
- Asynchronous database operations
- Batch processing for large datasets
- Pagination for efficient data retrieval
- Connection pooling

### Internationalization
- Multi-language template support
- Configurable default language
- Locale-specific response formatting

## Installation

### Prerequisites
- Python 3.10+
- PostgreSQL with pgvector extension
- Docker (for containerized services)

### Dependencies Installation

```bash
sudo apt update
sudo apt install libpq-dev gcc python3-dev
```

### Python Environment Setup

```bash
# Using Conda
conda create -n mini-rag python=3.10
conda activate mini-rag
```

### Required Packages

```bash
pip install -r requirements.txt
```

### Environment Configuration

```bash
cp .env.example .env
```

Edit the `.env` file to configure your environment variables including:
- Database credentials
- LLM API keys
- Service endpoints
- Security settings

### Database Migration

```bash
cd src/models/db_schemes/minirag
alembic upgrade head
```

### Docker Services

```bash
cd docker
cp .env.example .env
# Update .env with your credentials
docker compose up -d
```

## Running the Application

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Token refresh

### Data Management
- `POST /api/v1/data/upload/{project_id}` - Upload documents or process URLs
- `GET /api/v1/data/project/{project_id}/assets` - List project assets

### Natural Language Processing
- `POST /api/v1/nlp/index/push/{project_id}` - Index documents into vector database
- `POST /api/v1/nlp/search/{project_id}` - Perform semantic search on indexed documents

## Production Deployment Guidelines

For production deployments, consider the following recommendations:

1. **Security Hardening**
   - Rotate RSA keys regularly
   - Use strong, unique passwords for all services
   - Implement network segmentation and firewall rules
   - Enable SSL/TLS for all external communications

2. **Performance Optimization**
   - Use connection pooling for database connections
   - Configure appropriate timeouts and retry policies
   - Monitor resource utilization and scale accordingly
   - Implement caching for frequently accessed data

3. **Monitoring & Maintenance**
   - Set up centralized logging and monitoring
   - Implement automated backup strategies for databases
   - Regularly update dependencies and apply security patches
   - Establish alerting for critical system events

4. **Scalability Considerations**
   - Plan vector database capacity based on document volume
   - Consider sharding strategies for large datasets
   - Implement load balancing for high availability
   - Use CDN for static asset delivery when applicable

## Contributing

We welcome contributions from the community. Please see our contributing guidelines for information on how to submit bug reports, feature requests, and pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.