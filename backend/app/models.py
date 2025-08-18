from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300))
    price_raw = Column(String(100))
    price_num = Column(Float, nullable=True)     # numeric price (local currency / EUR as you decide)
    city = Column(String(100))
    year = Column(Integer, nullable=True)
    mileage_km = Column(Integer, nullable=True)
    url = Column(String(500))
    description = Column(Text)
