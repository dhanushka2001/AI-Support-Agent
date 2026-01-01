from fastapi import APIRouter
from app.services.document_repository import list_all_pdfs


router = APIRouter(prefix="/pdf", tags=["PDF List"])


@router.get("/list")
async def list_pdfs():
    return list_all_pdfs()
