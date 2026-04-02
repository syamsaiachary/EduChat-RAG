import chromadb
from app.core.config import settings

def get_chroma_client():
    return chromadb.PersistentClient(path="./chroma_db")

def get_chroma_collection():
    client = get_chroma_client()
    # Ensure distance metric is cosine as per PRD
    return client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"}
    )
