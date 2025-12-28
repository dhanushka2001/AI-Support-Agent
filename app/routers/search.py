from fastapi import APIRouter, HTTPException
from app.services.search_service import search_similar_chunks

router = APIRouter(prefix="/search", tags=["Vector Search"])


@router.post("/")
def vector_search(query: str, top_k: int = 5):
    try:
        results = search_similar_chunks(query, top_k)
        return {
            "query": query,
            "top_k": top_k,
            "results": results
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

