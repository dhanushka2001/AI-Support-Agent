from fastapi import APIRouter, HTTPException
from app.services.document_repository import get_document_text
from app.services.embedding_service import embed_and_store

router = APIRouter(prefix="/embeddings", tags=["Embeddings"])


@router.post("/{file_id}")
def generate_embeddings(file_id: str):
    text = get_document_text(file_id)
    if not text:
        raise HTTPException(status_code=404, detail="No extracted text found")

    count = embed_and_store(file_id, text)

    return {
        "file_id": file_id,
        "chunks_embedded": count
    }

