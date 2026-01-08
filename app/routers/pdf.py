from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from app.services.file_storage import save_pdf, get_pdf_path
from app.services.pdf_service import extract_text_from_pdf, PDFExtractionError
from app.services.embedding_service import embed_and_store
from app.services.document_repository import (
    create_document,
    store_extracted_text,
    get_document_by_file_id,
    delete_pdf_by_file_id,
    list_all_pdfs,
    get_document_text,
    update_embed_status,
    store_extracted_entities,
)
from app.services.entity_extractor import (
    extract_entities,
    extract_sentence_entity_edges,
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


@router.post("/extract/{file_id}")
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

        entities = extract_entities(text)

        entity_edges = extract_sentence_entity_edges(text)

        store_extracted_entities(file_id, entities, entity_edges)  # MongoDB

        return {
            "file_id": file_id,
            "text_length": len(text),
            "text_preview": text[:1000],  # prevent massive response
        }

    except PDFExtractionError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/embed/{file_id}")
def generate_embeddings(file_id: str):
    text = get_document_text(file_id)
    if not text:
        raise HTTPException(status_code=404, detail="No extracted text found")

    count = embed_and_store(file_id, text)
    
    update_embed_status(file_id, count)

    return {
        "file_id": file_id,
        "chunks_embedded": count
    }


@router.get("/list")
async def list_pdfs():
    return list_all_pdfs()


@router.delete("/{file_id}")
async def delete_pdf(file_id: str):
    return delete_pdf_by_file_id(file_id)
