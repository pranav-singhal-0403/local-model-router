# Local Model Router

A locally hosted Retrieval-Augmented Generation (RAG) chatbot for asking
questions about uploaded PDF documents. The application combines dense
vector retrieval, a local Ollama language model, and a React interface
with persistent conversation history.

## Features

-   **Local LLM inference:** Uses Ollama to run the configured language
    model locally.
-   **PDF ingestion:** Upload PDFs, extract and chunk their text,
    generate embeddings, and index chunks for retrieval.
-   **Semantic retrieval:** Uses dense embeddings and Qdrant to find
    relevant document chunks.
-   **Source references:** Answers include retrieved document names,
    page numbers, and relevance scores.
-   **Persistent chat history:** Stores conversations and messages in
    PostgreSQL, including sources and latency metadata.
-   **Conversation management:** Create chats, search chat titles,
    reopen previous conversations, and delete conversations.
-   **Document library:** View indexed PDFs, upload new files, and
    remove documents.
-   **Latency reporting:** Displays retrieval, generation, and total
    response time.
-   **Local service health:** Provides a health endpoint for checking
    the backend and its dependencies.

## Architecture

``` text
React + Vite frontend
        |
        | HTTP / JSON
        v
FastAPI backend
   |          |             |
   |          |             +--> PostgreSQL
   |          |                  Conversations and messages
   |          |
   |          +----------------> Ollama
   |                              Local LLM generation
   |
   +----------------------------> Qdrant
                                  Vector embeddings and document chunks
```

The frontend and backend run as separate development processes. Qdrant
and PostgreSQL run through Docker Compose. Ollama runs directly on the
host machine and is not part of Docker Compose.

## Technology Stack

  Component               Technology
  ----------------------- -------------------------------------------
  Frontend                React, Vite, JavaScript, CSS
  Backend API             Python, FastAPI
  Request validation      Pydantic
  Local language model    Ollama
  Default chat model      `gemma3:4b`
  Embeddings              `BAAI/bge-small-en-v1.5`
  Embedding dimension     384
  Vector database         Qdrant
  Conversation database   PostgreSQL 16
  PostgreSQL driver       asyncpg
  HTTP client             Axios / HTTPX
  PDF processing          Project PDF parser and ingestion pipeline
  Container services      Docker Compose

## Project Structure

``` text
local-model-router/
├── backend/
│   ├── api/
│   │   ├── chat.py
│   │   ├── documents.py
│   │   ├── health.py
│   │   └── history.py
│   ├── app_state.py
│   ├── answer_generator.py
│   ├── chat_history.py
│   ├── chunker.py
│   ├── config.py
│   ├── database.py
│   ├── embeddings_dense.py
│   ├── ingestion_pipeline.py
│   ├── main.py
│   ├── models.py
│   ├── ollama_client.py
│   ├── pdf_parser.py
│   ├── prompt_builder.py
│   ├── qdrant_client.py
│   └── retreiver_dense.py
├── config/
│   └── config.yml
├── documents/
├── extracted/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   ├── package.json
│   └── ...
├── docker-compose.yml
├── requirements.txt
├── .env
└── README.md
```

Some filenames or optional directories may differ depending on your
local checkout. Keep the names referenced by your actual imports and
configuration.

## Prerequisites

Install the following before starting:

-   **Python 3.11 or newer** compatible with the packages in
    `requirements.txt`
-   **Node.js and npm** compatible with the installed Vite version
-   **Docker Desktop** with Docker Compose
-   **Ollama** installed directly on the host
-   Git, if cloning the repository

For local LLM inference, ensure your machine has enough RAM/VRAM for the
model you choose.

## Configuration

### 1. Configure environment variables

Create or update the root `.env` file. Keep any existing project
variables and add the database and service settings below:

``` dotenv
POSTGRES_DB=rag_router
POSTGRES_USER=raguser
POSTGRES_PASSWORD=replace_with_a_strong_local_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

QDRANT_HOST=localhost
QDRANT_PORT=6333

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:4b
```

Use a strong local PostgreSQL password and keep `.env` out of version
control. Do not commit credentials or secrets. The backend also reads
application settings from `config/config.yml`; check that file for
embedding, retrieval, chunking, ingestion, paths, and prompt settings.

If your environment already defines `DATABASE_URL`, the database module
uses it instead of assembling a URL from the individual PostgreSQL
variables.

### 2. Configure Ollama

Start Ollama on the host and pull the configured model:

``` bash
ollama pull gemma3:4b
ollama list
```

Verify the Ollama API is reachable at `http://localhost:11434`. If you
choose a different model, update `OLLAMA_MODEL` or the relevant model
setting in your configuration.

### 3. Start Qdrant and PostgreSQL

From the repository root:

``` bash
docker compose up -d
docker compose ps
```

This starts the services declared in `docker-compose.yml`. With the
standard project configuration, Qdrant is available at
`http://localhost:6333` and PostgreSQL at `localhost:5432`.

Check logs if a service does not become healthy:

``` bash
docker compose logs qdrant
docker compose logs postgres
```

The Compose volumes preserve Qdrant and PostgreSQL data when containers
are restarted. To stop the services without deleting their data:

``` bash
docker compose down
```

Do not use `docker compose down -v` unless you intend to remove the
persistent volumes and their data.

## Installation

Open a terminal at the repository root.

### 1. Create and activate a Python virtual environment

Windows PowerShell:

``` powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Windows Command Prompt:

``` bat
python -m venv venv
venv\Scripts\activate.bat
```

Linux or macOS:

``` bash
python3 -m venv venv
source venv/bin/activate
```

If your existing environment is named differently, activate that
environment instead.

### 2. Install backend dependencies

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Ensure `asyncpg` is listed in `requirements.txt`, since PostgreSQL
access uses it.

### 3. Install frontend dependencies

``` bash
cd frontend
npm install
cd ..
```

## Run the Application

Start each service in the order below.

### 1. Start infrastructure

From the repository root:

``` bash
docker compose up -d
```

Confirm that Qdrant and PostgreSQL are running:

``` bash
docker compose ps
```

### 2. Start Ollama

Ensure the Ollama application/service is running on the host. Confirm
that the configured model is available:

``` bash
ollama list
```

### 3. Start the FastAPI backend

From the repository root, with the Python virtual environment activated:

``` bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API should be available at:

-   API root: `http://localhost:8000/`
-   Interactive API docs: `http://localhost:8000/docs`
-   Health endpoint: `http://localhost:8000/health`

The application lifespan initializes the RAG components and PostgreSQL
schema on startup. If startup fails, inspect the terminal output and
verify the `.env`, database, Qdrant, and Ollama configuration.

### 4. Start the frontend

Open another terminal:

``` bash
cd frontend
npm run dev
```

Open the URL printed by Vite, usually `http://localhost:5173`.

Keep the backend, frontend, Ollama, and Docker services running while
using the application.

## Using the Application

### Chat with PDFs

1.  Open **Documents**.
2.  Upload a PDF.
3.  Wait for ingestion and indexing to finish.
4.  Open **Chat** and start a new conversation.
5.  Ask a question about the indexed documents.
6.  Review the answer, source references, and latency information.

The quality of an answer depends on the extracted text, chunking,
embedding model, retrieval settings, and prompt configuration.

### Manage conversations

-   Select **New chat** to create a conversation.
-   Select a conversation in the sidebar to reopen its saved messages.
-   Search by conversation title.
-   Delete a conversation to remove its stored messages.
-   Refresh the browser to verify that PostgreSQL-backed history
    persists.

Conversation titles are generated from the first user message by the
backend.

### Manage documents

Use the document library to upload PDFs, view indexed documents, and
delete documents from the vector store and associated storage.

## API Endpoints

The main endpoints currently used by the frontend are listed below.

  ---------------------------------------------------------------------------------------------
  Method                  Endpoint                                      Purpose
  ----------------------- --------------------------------------------- -----------------------
  `GET`                   `/`                                           Basic API status

  `GET`                   `/health`                                     Check service health
                                                                        and configured models

  `POST`                  `/chat`                                       Retrieve relevant
                                                                        chunks and generate an
                                                                        answer

  `POST`                  `/documents/upload`                           Upload and ingest a PDF

  `GET`                   `/documents`                                  List indexed documents

  `DELETE`                `/documents/{document_id}`                    Delete a document

  `POST`                  `/conversations`                              Create a conversation

  `GET`                   `/conversations`                              List conversations

  `GET`                   `/conversations/{conversation_id}/messages`   Load conversation
                                                                        messages

  `DELETE`                `/conversations/{conversation_id}`            Delete a conversation
                                                                        and its messages
  ---------------------------------------------------------------------------------------------

Open `http://localhost:8000/docs` for the interactive API specification.

## Data Storage

-   **Qdrant:** Stores vector representations and payloads for document
    chunks.
-   **PostgreSQL:** Stores conversations and messages, including JSON
    metadata for sources and latency.
-   **Local document storage:** Holds uploaded PDFs and any extracted
    artifacts configured by the ingestion pipeline.
-   **Ollama:** Runs model inference locally; it is not a Docker Compose
    service in this project setup.

Back up the PostgreSQL and Qdrant volumes, along with any local document
storage, if the indexed corpus and chat history must be recoverable.

## Troubleshooting

### Backend cannot connect to PostgreSQL

-   Check that the PostgreSQL container is running: `docker compose ps`.
-   Inspect logs: `docker compose logs postgres`.
-   Verify `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`,
    `POSTGRES_USER`, and `POSTGRES_PASSWORD`.
-   Ensure port `5432` is not already occupied.
-   If you changed the credentials after the PostgreSQL volume was
    initialized, update the existing database credentials or recreate
    the database volume only if its data can be discarded. Changing
    Compose environment variables alone does not reset an existing
    database user's password.

### Backend cannot connect to Qdrant

-   Check `docker compose ps` and `docker compose logs qdrant`.
-   Verify `QDRANT_HOST=localhost` and `QDRANT_PORT=6333` when the
    backend runs directly on the host.
-   Check that port `6333` is available.

### Ollama or model errors

-   Verify Ollama is running.
-   Run `ollama list` and confirm the configured model is installed.
-   Check `OLLAMA_BASE_URL` and `OLLAMA_MODEL`.
-   Make sure the host has enough memory for the selected model.

### Frontend cannot reach the backend

-   Confirm the backend is running on port `8000`.
-   The current frontend API client uses `http://localhost:8000`.
-   Ensure the backend CORS configuration permits the frontend origin,
    normally `http://localhost:5173`.

### Conversations do not appear or messages fail to load

-   Check the backend logs and PostgreSQL health.
-   Open the `/conversations` endpoints in `http://localhost:8000/docs`.
-   Verify that the frontend is using the same backend base URL for chat
    and conversation endpoints.

### PDF ingestion fails

-   Check the backend logs for parsing, chunking, embedding, or Qdrant
    errors.
-   Confirm the file is a supported PDF and that the configured
    embedding model can be loaded.
-   Check available disk space and memory.

## Development Notes

-   Run the backend from the repository root so the `backend` package
    and `config/config.yml` can be resolved.
-   Keep secrets in `.env`; commit an `.env.example` containing
    placeholders rather than real credentials.
-   Avoid deleting Docker volumes during routine restarts.
-   If changing the embedding model or vector dimension, verify the
    Qdrant collection configuration and re-ingest documents as required.
-   If changing API request or response models, update the frontend API
    service and related components together.

## License

Add the license and usage terms applicable to this repository before
publishing it publicly.
