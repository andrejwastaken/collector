from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal

class CarOut(BaseModel):
    id: int
    image_url: str | None
    title: str | None
    url: str | None
    make: str | None
    model: str | None
    city: str | None
    municipality: str | None
    price_num: Decimal | None
    year: int | None
    mileage_km: int | None
    date_posted: datetime | None
    scraped_at: datetime | None
    
    model_config = ConfigDict(from_attributes=True)

class RetrievedCar(BaseModel):
    id: int
    distance: float
    metadata: dict
    document: str

class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    
class SearchResponse(BaseModel):
    answer: str
    retrieved_cars: list[RetrievedCar]
    cars: list[CarOut]

    model_config = {"from_attributes": True}
    
class UserCreate(BaseModel):
    username: str
    password: str

class MessageCreate(BaseModel):
    user_id: int
    message: str