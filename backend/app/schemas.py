from pydantic import BaseModel, ConfigDict

class CarOut(BaseModel):
    id: int
    title: str | None
    price_num: float | None
    city: str | None
    year: int | None
    mileage_km: int | None
    url: str | None
    model_config = ConfigDict(from_attributes=True)
