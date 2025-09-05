import chromadb

from chromadb.config import Settings

client = chromadb.PersistentClient(
    path="/app/chroma_db"
)

collection = client.get_or_create_collection(
    "cars_embeddings",
    metadata={"hnsw:space": "cosine"}
)

nums_docs = len(collection.get())
print(f"Number of documents in ChromaDB: {nums_docs}")