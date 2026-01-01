from datetime import datetime
from app.db.mongodb import documents_collection


def create_document(metadata: dict) -> dict:
    document = {
        "file_id": metadata["file_id"],
        "original_filename": metadata["filename"],
	    "file_hash": metadata["file_hash"],
        # "stored_filename": metadata["stored_filename"],
        "size_bytes": metadata["size_bytes"],
        "content_type": metadata["content_type"],
        "status": "UPLOADED",
        "created_at": datetime.utcnow(),
    }

    documents_collection.insert_one(document)
    return document


def get_document_by_file_id(file_id: str) -> dict | None:
    return documents_collection.find_one({"file_id": file_id})


def store_extracted_text(file_id: str, text: str):
    result = documents_collection.update_one(
        {"file_id": file_id},
        {
            "$set": {
                "extracted_text": text,
                "status": "EXTRACTED",
                "extracted_at": datetime.utcnow(),
            }
        }
    )

    if result.matched_count == 0:
        raise ValueError("Document not found")


def get_document_text(file_id: str) -> str | None:
    doc = documents_collection.find_one(
        {"file_id": file_id},
        {"extracted_text": 1}
    )
    return doc.get("extracted_text") if doc else None


def list_all_pdfs():
    return list(documents_collection.find(
        {}, 
        {
            "_id": 0,
            "extracted_text": 0,
            "stored_filename": 0,
            "content_type": 0
        }
    ))

def delete_pdf_by_file_id(file_id: str):
    pdf = documents_collection.find_one({"file_id": file_id})

    if not pdf:
        raise HTTPException(404, "PDF not found")

    # 1. Delete file from disk
    # 2. Delete chunks from Qdrant
    # 3. Delete DB record

    documents_collection.delete_one({"file_id": file_id})

    return {"ok": True}
