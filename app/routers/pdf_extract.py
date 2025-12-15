from fastapi import APIRouter, HTTPException
from pathlib import Path


from app.services.file_storage import get_pdf_path
from app.services.pdf_service import extract_text_from_pdf, PDFExtractionError
from app.services.document_repository import (
    store_extracted_text,
    get_document_by_file_id,
)


router = APIRouter(prefix="/pdf", tags=["PDF Extraction"])


@router.post("/{file_id}/extract")
def extract_pdf_text(file_id: str):
    document = get_document_by_file_id(file_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.get("status") == "EXTRACTED":
        return {
            "message": "Text already extracted",
            "file_id": file_id,
        }

    try:
        pdf_path = Path(get_pdf_path(file_id))
        text = extract_text_from_pdf(pdf_path)

        store_extracted_text(file_id, text)  # MongoDB

        return {
            "file_id": file_id,
            "text_length": len(text),
            "text_preview": text[:1000],  # prevent massive response
        }

    except PDFExtractionError as e:
        raise HTTPException(status_code=422, detail=str(e))
