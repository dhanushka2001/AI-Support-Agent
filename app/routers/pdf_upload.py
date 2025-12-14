from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.file_storage import save_pdf


router = APIRouter(prefix="/pdf", tags=["PDF Upload"])


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    metadata = save_pdf(file)
    
    return {
        "message": "PDF uploaded successfully",
        "metadata": metadata
    }
