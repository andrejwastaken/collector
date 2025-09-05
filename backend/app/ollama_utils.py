from ollama import Client

client = Client()

def get_embedding(text: str) -> list[float]:
    try:
        response = client.embeddings(model="nomic-embed-text", prompt=text)
        return response["embedding"]
    except Exception as e:
        raise RuntimeError(f"Embedding generation failed: {e}")
