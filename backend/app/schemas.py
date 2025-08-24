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
