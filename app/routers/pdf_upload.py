from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.file_storage import save_pdf
from app.services.document_repository import create_document


router = APIRouter(prefix="/pdf", tags=["PDF Upload"])


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    metadata = save_pdf(file)
    document = create_document(metadata)

    return {
        # "message": "PDF uploaded successfully",
        # "metadata": metadata,
        "file_id": document["file_id"],
        "original_filename": document["original_filename"],
        "status": document["status"]
    }
