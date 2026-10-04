from pathlib import Path
import os
import yaml
from dotenv import load_dotenv

load_dotenv(override=True)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "config.yml"


with open(CONFIG_PATH, "r", encoding="utf-8") as file:
    CONFIG = yaml.safe_load(file)


APP_CONFIG = CONFIG["app"]
LLM_CONFIG = CONFIG["ollama"]
EMBEDDING_CONFIG = CONFIG["embeddings"]
VECTORSTORE_CONFIG = CONFIG["vectorstore"]
RETRIEVAL_CONFIG = CONFIG["retrieval"]
CHUNKING_CONFIG = CONFIG["chunking"]
INGESTION_CONFIG = CONFIG["ingestion"]
PATH_CONFIG = CONFIG["paths"]


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    LLM_CONFIG["base_url"],
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    LLM_CONFIG["model"],
)

QDRANT_HOST = os.getenv(
    "QDRANT_HOST",
    VECTORSTORE_CONFIG["host"],
)

QDRANT_PORT = int(
    os.getenv(
        "QDRANT_PORT",
        VECTORSTORE_CONFIG["port"],
    )
)

QDRANT_COLLECTION = os.getenv(
    "QDRANT_COLLECTION",
    VECTORSTORE_CONFIG["collection_name"],
)


DOCUMENTS_DIR = PROJECT_ROOT / PATH_CONFIG["documents"]
EXTRACTED_DIR = PROJECT_ROOT / PATH_CONFIG["extracted"]

DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)