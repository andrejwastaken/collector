from ollama import Client

client = Client()

def get_embedding(text: str, retries: int = 3) -> list[float]:
    for attempt in range(retries):
        try:
            response = client.embeddings(model="bge-m3", prompt=text)
            return response["embedding"]
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
    raise RuntimeError(f"Embedding generation failed after {retries} attempts.")

