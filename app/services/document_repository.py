from datetime import datetime
from app.db.mongodb import documents_collection


def create_document(metadata: dict) -> dict:
    document = {
        "file_id": metadata["file_id"],
        "original_filename": metadata["filename"],
        "stored_filename": metadata["stored_filename"],
        "size_bytes": metadata["size_bytes"],
        "content_type": metadata["content_type"],
        "status": "UPLOADED",
        "created_at": datetime.utcnow(),
    }

    documents_collection.insert_one(document)
    return document

