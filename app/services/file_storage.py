import os
import uuid
import hashlib
from fastapi import UploadFile
from app.core.errors import (
    unsupported_file, 
    bad_request, 
    duplicate_file,
)
from app.db.mongodb import db

# Base storage folder
BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "pdfs")

# Ensure directory exists
os.makedirs(BASE_DIR, exist_ok=True)


def validate_pdf(file: UploadFile):
    # Check presence
    if file is None:
        raise bad_request("No file was uploaded.")

    # Validate extension
    filename = file.filename.lower()
    if not filename.endswith(".pdf"):
        raise unsupported_file("File extension must be .pdf")

    # Validate MIME type
    if file.content_type != "application/pdf":
        raise unsupported_file("Invalid file type. Only PDF files are allowed.")

    return True


def save_pdf(file: UploadFile) -> dict:
    # Validate PDF
    validate_pdf(file)

    # Generate unique filename
    file_id = str(uuid.uuid4())
    filename = f"{file_id}.pdf"
    filepath = os.path.join(BASE_DIR, filename)

    #  Read file bytes
    file_bytes = file.file.read()

    # Save file data
    with open(filepath, "wb") as out_file:
        out_file.write(file_bytes)

    # Reset pointer so file can be re-read if needed later
    file.file.seek(0)

    # Duplicate pdf
    file_hash = compute_file_hash(file)
    existing = db.documents.find_one({"file_hash": file_hash})
    if existing:
        raise duplicate_file("This PDF has already been uploaded.")

    # Return metadata
    return {
        "file_id": file_id,
        "filename": file.filename,
        "file_hash": file_hash,
        "stored_filename": filename,
        "path": filepath,
        "size_bytes": os.path.getsize(filepath),
        "content_type": file.content_type,
    }


def get_pdf_path(file_id: str) -> str:
    filename = f"{file_id}.pdf"
    filepath = os.path.join(BASE_DIR, filename)

    if not os.path.exists(filepath):
        raise bad_request("PDF not found.")

    return filepath


def compute_file_hash(file: UploadFile) -> str:
    hasher = hashlib.sha256()
    for chunk in iter(lambda: file.file.read(8192), b""):
        hasher.update(chunk)
    file.file.seek(0)
    return hasher.hexdigest()
