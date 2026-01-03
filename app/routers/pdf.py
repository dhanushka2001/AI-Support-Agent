from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.file_storage import save_pdf, get_pdf_path
from app.services.pdf_service import extract_text_from_pdf, PDFExtractionError
from app.services.document_repository import (
    create_document,
    store_extracted_text,
    get_document_by_file_id,
    delete_pdf_by_file_id,
    list_all_pdfs,
)


router = APIRouter(prefix="/pdf", tags=["PDF"])


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


@router.get("/list")
async def list_pdfs():
    return list_all_pdfs()


@router.delete("/{file_id}")
async def delete_pdf(file_id: str):
    return delete_pdf_by_file_id(file_id)
