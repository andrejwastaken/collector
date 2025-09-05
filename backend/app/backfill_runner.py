from app.main import get_db
from app.backfill import backfill_embeddings

def main():
    db = next(get_db())
    backfill_embeddings(db)

if __name__ == "__main__":
    main()
