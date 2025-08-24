from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String(500))
    title = Column(String(300))
    url = Column(String(500))
    make = Column(String(100))
    model = Column(String(100))
    city = Column(String(100))
    municipality = Column(String(100))
    price_num = Column(Float, nullable=True)
    year = Column(Integer, nullable=True)
    mileage_km = Column(Float, nullable=True)
    date_posted = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

