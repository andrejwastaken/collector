from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
from sqlalchemy.orm import relationship

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

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    chats = relationship("Chat", back_populates="owner")

class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="chats")