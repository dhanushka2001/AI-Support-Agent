from fastapi import APIRouter, HTTPException
from app.services.file_storage import get_pdf_path
from app.services.pdf_service import extract_text_from_pdf, PDFExtractionError
from pathlib import Path

router = APIRouter(prefix="/pdf", tags=["PDF Extraction"])


@router.post("/{file_id}/extract")
def extract_pdf_text(file_id: str):
    try:
        pdf_path = Path(get_pdf_path(file_id))
        text = extract_text_from_pdf(pdf_path)

        return {
            "file_id": file_id,
            "text_length": len(text),
            "text_preview": text[:1000],  # prevent massive response
        }

    except PDFExtractionError as e:
        raise HTTPException(status_code=422, detail=str(e))

