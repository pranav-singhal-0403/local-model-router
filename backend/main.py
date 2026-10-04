from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.chat import router as chat_router
from backend.api.documents import router as documents_router
from backend.api.health import router as health_router


app = FastAPI(
    title="Pranav Singhal Local Model Router",
    version="0.1.0",
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
    health_router,
)

app.include_router(
    documents_router,
)

app.include_router(
    chat_router,
)


@app.get("/")
async def root():

    return {
        "name": "Local Model Router",
        "version": "0.1.0",
        "status": "running",
    }