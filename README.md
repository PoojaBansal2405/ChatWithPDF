# ChatWithPDF — AI-Powered Document Question Answering

ChatWithPDF is an AI-powered document question-answering system built using **Retrieval-Augmented Generation (RAG)**. It enables users to interact with PDF documents through natural language queries and receive relevant, context-based answers.

The system combines document processing, semantic search, vector embeddings, and Large Language Models (LLMs) to retrieve relevant information from uploaded documents and generate meaningful responses.

Built with FastAPI, ChromaDB, MongoDB, Sentence Transformers, and Groq, the project focuses on developing a modular backend architecture for intelligent document retrieval and question answering.

---

## Key Features

- **PDF Document Upload:** Upload PDF documents through REST APIs built with FastAPI.
- **Text Extraction:** Extract textual content from PDF documents using PyMuPDF.
- **Text Chunking:** Divide extracted text into smaller chunks for efficient retrieval.
- **Embedding Generation:** Generate dense vector embeddings using Sentence Transformers.
- **Vector Storage:** Store document embeddings and associated metadata using ChromaDB.
- **Semantic Search:** Retrieve relevant document chunks based on the semantic similarity of user queries.
- **LLM-Powered Responses:** Generate natural language answers using Groq-hosted Large Language Models.
- **Document Management:** Store and manage document metadata using MongoDB.
- **Modular Backend:** Separate API routes, business logic, database operations, and RAG components.
- **Interactive API Documentation:** Explore and test backend endpoints through FastAPI Swagger UI.

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | Backend REST API development |
| ChromaDB | Vector database and similarity search |
| MongoDB | Document metadata management |
| Sentence Transformers | Text embedding generation |
| all-MiniLM-L6-v2 | Embedding model |
| Groq | LLM inference |
| LangChain | LLM integration |
| PyMuPDF | PDF text extraction |
| Uvicorn | ASGI server |

---

## System Architecture

ChatWithPDF follows a Retrieval-Augmented Generation (RAG) architecture consisting of two primary workflows.

### 1. Document Ingestion Pipeline

When a PDF document is uploaded:

1. The document is received through a FastAPI endpoint.
2. Text is extracted from the PDF using PyMuPDF.
3. Extracted text is divided into smaller chunks.
4. Sentence Transformers generates vector embeddings for each chunk.
5. Generated embeddings and associated metadata are stored in ChromaDB.
6. Document metadata is maintained in MongoDB.

### 2. Question Answering Pipeline

When a user submits a question:

1. The query is converted into a vector embedding using the same embedding model.
2. ChromaDB performs semantic similarity search against stored document embeddings.
3. Relevant document chunks are retrieved.
4. Retrieved information is passed as context to the LLM.
5. The LLM generates a natural language response using the retrieved document context.

### Architecture Flow

```text
                 DOCUMENT INGESTION

                  PDF Upload
                       |
                       v
                  FastAPI API
                       |
                       v
              PDF Text Extraction
                       |
                       v
                 Text Chunking
                       |
                       v
              Embedding Generation
                       |
                       v
                   ChromaDB
                (Vector Storage)

              MongoDB (Metadata)


                 QUERY PROCESSING

                  User Query
                       |
                       v
                Query Embedding
                       |
                       v
               Semantic Retrieval
                       |
                       v
             Relevant Document Chunks
                       |
                       v
                 Context + Prompt
                       |
                       v
                    Groq LLM
                       |
                       v
                Generated Answer
```

---

## Project Structure

```text
ChatWithPDF/
│
├── backend/
│   │
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   ├── dependencies.py
│   │   │   └── routes/
│   │   │       ├── chat.py
│   │   │       ├── documents.py
│   │   │       └── notebooks.py
│   │   │
│   │   ├── core/
│   │   │   └── database.py
│   │   │
│   │   ├── db/
│   │   │   └── mongodb.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── chat.py
│   │   │   └── notebook.py
│   │   │
│   │   └── services/
│   │       ├── chat_service.py
│   │       ├── document_service.py
│   │       └── notebook_service.py
│   │
│   ├── src/
│   │   ├── data_loader.py
│   │   ├── embedding.py
│   │   ├── rag.py
│   │   ├── retriever.py
│   │   ├── search.py
│   │   ├── vectorstore.py
│   │   └── vectorstore2.py
│   │
│   ├── data/
│   │   └── uploads/
│   │
│   ├── requirements.txt
│   └── .env
│
└── README.md
```

### Backend Architecture

The backend follows a modular architecture with separation of responsibilities.

| Directory / Module | Responsibility |
|---|---|
| `app/api/routes/` | API endpoints for document, chat, and notebook operations |
| `app/api/dependencies.py` | Shared API dependencies |
| `app/core/` | Core application configuration and database setup |
| `app/db/` | MongoDB connection management |
| `app/schemas/` | Request and response data models |
| `app/services/` | Business logic for document, chat, and notebook operations |
| `src/data_loader.py` | PDF loading and text extraction |
| `src/embedding.py` | Text and query embedding generation |
| `src/retriever.py` | Retrieval of relevant document chunks |
| `src/search.py` | Semantic search functionality |
| `src/vectorstore.py` | Vector database operations |
| `src/rag.py` | Retrieval-Augmented Generation pipeline |

---

## Installation and Setup

### Prerequisites

- Python 3.10 or later
- MongoDB instance (local or MongoDB Atlas)
- Groq API key

### 1. Clone the Repository

```bash
git clone https://github.com/PoojaBansal2405/ChatWithPDF.git

cd ChatWithPDF
```

### 2. Navigate to the Backend

```bash
cd backend
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the virtual environment:

**Windows**

```bash
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

### 4. Install Dependencies

Install the Python packages required by the application:

```bash
pip install -r requirements.txt
```

Ensure that `requirements.txt` includes all third-party dependencies imported by the backend.

### 5. Configure Environment Variables

Create a `.env` file inside the `backend/` directory.

Add the following configuration:

```env
groq_api_key=your_groq_api_key
MONGODB_URI=your_mongodb_connection_string
MONGODB_DB=your_database_name
```

Replace the placeholder values with your actual credentials.

**Important:** Never commit your `.env` file or expose API keys in your GitHub repository.

### 6. Run the Backend

From the `backend/` directory, start the FastAPI application:

```bash
uvicorn app.main:app --reload
```

### 7. Access API Documentation

Once the server is running, access the interactive API documentation:

**Swagger UI**

http://127.0.0.1:8000/docs

**ReDoc**

http://127.0.0.1:8000/redoc

---

## API Functionality

The backend is organized around three primary API modules:

| API Module | Responsibility |
|---|---|
| Documents | PDF upload and document management |
| Chat | Document-based question answering |
| Notebooks | Notebook-related operations |

For available endpoints, request parameters, and response formats, refer to the interactive Swagger documentation at `/docs`.

---

## Current Development Status

### Implemented

- PDF document upload and ingestion.
- PDF text extraction and chunking.
- Embedding generation using Sentence Transformers.
- Vector storage and semantic retrieval using ChromaDB.
- MongoDB integration for document metadata.
- FastAPI backend with modular API routes and service layers.
- Groq LLM integration for RAG-based answer generation.

### In Progress

- Conversational memory and chat history management.
- Maintaining context across multiple questions.
- Expanded testing and edge-case handling.
- Frontend development.

### Planned Enhancements

- Multi-turn conversational question answering.
- Persistent conversation history.
- Source citations and references in generated answers.
- Interactive frontend for document conversations.
- Retrieval optimization and improved response quality.

---

## Future Scope

The long-term goal is to evolve ChatWithPDF into a complete AI-powered document assistant.

Future development will focus on conversational RAG, persistent chat management, improved retrieval techniques, and an interactive user experience.

---

## Author

**Pooja Bansal**

B.Tech Computer Science and Engineering

GitHub: [@PoojaBansal2405](https://github.com/PoojaBansal2405)

---

*Built to explore Retrieval-Augmented Generation, semantic search, vector databases, backend engineering, and practical applications of Large Language Models.*
