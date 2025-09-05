from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi import HTTPException as HttpException
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

@app.get("/cars/{car_id}", response_model=CarOut)
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HttpException(status_code=404, detail="Car not found")
    return car