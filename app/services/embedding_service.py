import uuid
from openai import OpenAI
from app.db.qdrant import get_qdrant_client


client = OpenAI()


COLLECTION_NAME = "documents_embeddings"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
EMBEDDING_MODEL = "text-embedding-3-small"


def chunk_text(text: str):
    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end])
        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def embed_and_store(file_id: str, text: str):
    if not text:
        raise ValueError("No extracted text found")


    chunks = chunk_text(text)

    qdrant_client = get_qdrant_client()

    embeddings = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=chunks
    )


    points = []
    for idx, emb in enumerate(embeddings.data):
        base_uuid = uuid.UUID(file_id)
        point_id = uuid.uuid5(base_uuid, str(idx))
        
        points.append({
            # "id": str(uuid.uuid4()), # valid UUID but not deterministic
            # "id": f"{file_id}_{idx}", # deterministic but not valid UUID
            "id": str(point_id), # valid UUID and deterministic
            "vector": emb.embedding,
            "payload": {
                "file_id": file_id,
                "chunk_index": idx,
                "text": chunks[idx],
            }
        })

    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    return len(points)

