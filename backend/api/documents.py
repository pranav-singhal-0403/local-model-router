from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, Request

from backend.config import DOCUMENTS_DIR


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

@router.get("")
async def list_documents(request: Request):
    try:
        state = request.app.state.rag
        documents = state.qdrant.list_documents()
        return {
            "documents": documents,
            "total": len(documents),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list documents : {e}"
        )

@router.post("/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided.",
        )
    
    original_name = Path(file.filename).name

    if Path(original_name).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    safe_name = (
        f"{uuid4()}_{original_name}"
    )

    destination = DOCUMENTS_DIR / safe_name

    try:

        content = await file.read()
        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )
        destination.write_bytes(content)

        state = request.app.state.rag
        result = state.ingestion.ingest_pdf(
            destination,
            display_name=original_name,
        )

        return {
            "status": "success",
            "message": "Document uploaded and indexed.",
            "filename": original_name,
            "stored_filename": safe_name,
            "ingestion": result,
        }
    except HTTPException:
        if destination.exists():
            destination.unlink()
        raise

    except Exception as exc:

        if destination.exists():
            destination.unlink()

        raise HTTPException(
            status_code=500,
            detail=f"Document ingestion failed : {exc}",
        )

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    request: Request,
):
    try:
        state = request.app.state.rag
        documents = state.qdrant.list_documents()

        document = next(
            (
                item
                for item in documents
                if item["document_id"] == document_id
            ),
            None,
        )

        if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found.",
            )

        stored_filename = Path(
            document["stored_filename"]
        ).name

        if not stored_filename:
            raise HTTPException(
                status_code=500,
                detail="Stored filename is unavailable.",
            )

        state.qdrant.delete_document(document_id)

        file_path = DOCUMENTS_DIR / stored_filename

        if file_path.exists():
            file_path.unlink()

        return {
            "status": "success",
            "message": "Document and indexed chunks deleted.",
            "document_id": document_id,
            "document_name": document["document_name"],
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {exc}",
        )