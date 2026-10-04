from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.config import DOCUMENTS_DIR
from backend.ingestion_pipeline import IngestionPipeline


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided.",
        )

    extension = Path(file.filename).suffix.lower()

    if extension != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    safe_name = (
        f"{uuid4()}_{Path(file.filename).name}"
    )

    destination = DOCUMENTS_DIR / safe_name

    try:

        content = await file.read()

        destination.write_bytes(content)

        pipeline = IngestionPipeline()

        result = pipeline.ingest_pdf(
            destination
        )

        return {
            "status": "success",
            "message": "Document uploaded and indexed.",
            "filename": file.filename,
            "stored_filename": safe_name,
            "ingestion": result,
        }

    except Exception as exc:

        if destination.exists():
            destination.unlink()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )