import os
import uuid
from fastapi import UploadFile
from app.core.errors import unsupported_file, bad_request

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

    # Save file data
    with open(filepath, "wb") as out_file:
        out_file.write(file.file.read())

    # Return metadata
    return {
        "file_id": file_id,
        "filename": filename,
        "size_bytes": os.path.getsize(filepath),
        "content_type": file.content_type,
        "storage_path": filepath,
    }
