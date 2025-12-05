from fastapi import APIRouter
import fastapi
import datetime

router = APIRouter()

@router.get("/health")
async def health():
    return {
        "FastAPI version": fastapi.__version__,
        "Timestamp": datetime.datetime.now()
    }

