from typing import Optional
from pydantic import BaseModel
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
    
    model_config = {"from_attributes": True}

class RetrievedCar(BaseModel):
    id: int
    distance: float
    metadata: dict

class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    user_id: Optional[int] = None
    
class SearchResponse(BaseModel):
    answer: str
    retrieved_cars: list[RetrievedCar]

    model_config = {"from_attributes": True}
    
class UserCreate(BaseModel):
    username: str
    password: str

class ChatCreate(BaseModel):
    user_id: int
    message: str = ""
    title: Optional[str] = None