from fastapi import APIRouter
from app.db.qdrant import get_qdrant_client


router = APIRouter(prefix="/qdrant", tags=["Qdrant"])


@router.get("/health")
def qdrant_health():
    try:
        qdrant_client = get_qdrant_client()
        qdrant_client.get_collections()
        return {"qdrant": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
