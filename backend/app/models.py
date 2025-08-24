from sqlalchemy import Column, Integer, String, Numeric, DateTime
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
    price_num = Column(Numeric(10, 2), nullable=True)
    year = Column(Integer, nullable=True)
    mileage_km = Column(Integer, nullable=True)
    date_posted = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

