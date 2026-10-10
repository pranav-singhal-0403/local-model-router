from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.chat import router as chat_router
from backend.api.documents import (
    router as documents_router,
)
from backend.api.health import (
    router as health_router,
)
from backend.app_state import create_app_state
from backend.database import Database
from backend.chat_history import ChatHistory
from backend.api.history import router as history_router

@asynccontextmanager
async def lifespan(app: FastAPI):

    print(
        "[STARTUP] Initializing RAG components..."
    )

    app.state.rag = create_app_state()
    database = Database()
    await database.connect()

    app.state.database = database
    app.state.chat_history = ChatHistory(database)

    print(
        "[STARTUP] RAG components initialized."
    )

    try:
        yield
    finally:
        await database.close()

        if app.state.rag:
            await app.state.rag.ollama.close()

        app.state.rag = None
        app.state.database = None
        app.state.chat_history = None

        print("[SHUTDOWN] Resources released.")


app = FastAPI(
    title="Pranav Singhal Local Model Router",
    version="0.1.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    health_router
)

app.include_router(
    documents_router
)

app.include_router(
    chat_router
)

app.include_router(
    history_router
)

@app.get("/")
async def root():

    return {
        "name": "Local Model Router",
        "version": "0.1.0",
        "status": "running",
    }