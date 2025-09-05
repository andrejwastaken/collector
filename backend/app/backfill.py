from sqlalchemy.orm import Session
from app.models import Car
from app.chroma_client import collection
from app.ollama_utils import get_embedding
import time

BATCH_SIZE = 10  # process 500 cars at a time to save memory

def sanitize_metadata(metadata: dict):
    sanitized = {}
    for k, v in metadata.items():
        if v is None:
            if k in ["title", "make", "model", "city", "municipality"]:
                sanitized[k] = ""
            elif k in ["year", "price_num", "mileage_km"]:
                sanitized[k] = 0
            else:
                sanitized[k] = "N/A"
        else:
            sanitized[k] = v
    return sanitized


def backfill_embeddings(db: Session):
    offset = 0
    while True:
        if offset == 10:
            break
        cars = db.query(Car).offset(offset).limit(BATCH_SIZE).all()
        if not cars:
            break

        embeddings_to_add = []
        ids_to_add = []
        metadatas_to_add = []
        documents_to_add = []

        for car in cars:
            text_to_embed = f"{car.title}. Make: {car.make}, Model: {car.model}, Year: {car.year}, Mileage: {car.mileage_km} km, City: {car.city}, Price: {car.price_num}."

            try:
                embedding = get_embedding(text_to_embed)
            except Exception as e:
                print(f"Failed to embed car {car.id}: {e}")
                continue

            ids_to_add.append(str(car.id))
            embeddings_to_add.append(embedding)
            print(f"Embedded car {car.id}")
            print(embedding)
            # Sanitize the metadata dictionary for the current car
            car_metadata = {
                "id": car.id,
                "title": car.title,
                "make": car.make,
                "model": car.model,
                "city": car.city,
                "municipality": car.municipality,
                "year": car.year,
                "price_num": float(car.price_num) if car.price_num else None,
                "mileage_km": car.mileage_km
            }
            sanitized_car_metadata = sanitize_metadata(car_metadata)
            print(sanitized_car_metadata)
            metadatas_to_add.append(sanitized_car_metadata)

            documents_to_add.append(text_to_embed)

        # Add batch to Chroma
        if embeddings_to_add:
            collection.add(
                ids=ids_to_add,
                embeddings=embeddings_to_add,
                metadatas=metadatas_to_add,
                documents=documents_to_add
            )
            print(f"Added {len(embeddings_to_add)} embeddings to ChromaDB")

        print(f"Processed batch {offset} to {offset + len(cars)}")
        offset += BATCH_SIZE

        time.sleep(0.5)

    print("Backfill complete!")
