import chromadb

from chromadb.config import Settings

client = chromadb.PersistentClient(
    path="/app/chroma_db"
)

collection = client.get_or_create_collection(
    "cars_embeddings",
    metadata={"hnsw:space": "cosine"}
)

docs = collection.get()
nums_docs = len(docs['ids'])  # Count of documents
print(f"Number of documents in ChromaDB: {nums_docs}")