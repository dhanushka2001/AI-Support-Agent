from openai import OpenAI
from qdrant_client.models import ScoredPoint
from app.db.qdrant import get_qdrant_client, COLLECTION_NAME
from app.core.embeddings import EMBEDDING_MODEL

client = OpenAI()

def search_similar_chunks(query: str, top_k: int = 5):
    qdrant_client = get_qdrant_client()

    # 1. Embed the query
    query_embedding = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query
    ).data[0].embedding

    # 2. Query Qdrant
    results: list[ScoredPoint] = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=top_k,
    ).points

    # 3. Shape response
    return [
        {
            "score": point.score,
            "file_id": point.payload["file_id"],
            "chunk_index": point.payload["chunk_index"],
            "text": point.payload["text"],
        }
        for point in results
    ]

