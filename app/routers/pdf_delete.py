from fastapi import APIRouter
from app.services.document_repository import delete_pdf_by_file_id


router = APIRouter(prefix="/pdf", tags=["PDF Delete"])


@router.delete("/{file_id}")
async def delete_pdf(file_id: str):
    return delete_pdf_by_file_id(file_id)
