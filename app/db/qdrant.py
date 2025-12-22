from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

COLLECTION_NAME = "documents_embeddings"
VECTOR_SIZE = 1536  # OpenAI embedding dimension


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        host=QDRANT_HOST,
        port=QDRANT_PORT,
    )


def create_collection_if_not_exists():
    qdrant_client = get_qdrant_client()
    collections = qdrant_client.get_collections().collections
    existing_names = {c.name for c in collections}

    if COLLECTION_NAME in existing_names:
        return  # already exists

    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
    )

