from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import Car
from app.schemas import CarOut

app = FastAPI(title="Collector API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/cars", response_model=list[CarOut])
def list_cars(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Car).order_by(Car.price_num.asc().nulls_last()).limit(limit).all()
