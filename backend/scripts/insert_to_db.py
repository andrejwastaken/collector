import pandas as pd
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from app.db.session import SessionLocal  
from app.models import Car   
import numpy as np 

def insert_cleaned_to_db(df=None, csv_path=None):
    """
    Insert cleaned cars into the database.
    Either pass a DataFrame via `df` or a CSV path via `csv_path`.
    Avoids duplicates based on title + mileage + year.
    """
    if df is None and csv_path is not None:
        df = pd.read_csv(csv_path, encoding='utf-8-sig', keep_default_na=False)
    elif df is None and csv_path is None:
        raise ValueError("You must provide either a DataFrame or a CSV path")

    # Replace NaNs with None for SQLAlchemy
    df = df.replace({np.nan: None})
    session = SessionLocal()
    cars_to_insert = []

    try:
        # Pre-fetch existing cars as tuples of (title, mileage, year)
        existing_cars = set(
            session.query(Car.title, Car.mileage_km, Car.year).all()
        )

        for _, row in df.iterrows():
            year_value = row.get('year') if pd.notna(row.get('year')) else None
            mileage_value = row.get('mileage') if pd.notna(row.get('mileage')) else None

            price_raw = row.get('price')
            price_value = None
            if pd.notna(price_raw):
                try:
                    price_value = Decimal(str(price_raw)).quantize(Decimal("0.01"))
                except (InvalidOperation, ValueError):
                    price_value = None

            car_key = (
                row.get('title', None),
                mileage_value,
                year_value
            )
            if car_key in existing_cars:
                continue  # skip duplicates

            car = Car(
                image_url=row.get('image_url', None),
                title=row.get('title', None),
                url=row.get('url', None),
                price_num=price_value,
                year=year_value,
                mileage_km=mileage_value,
                date_posted=pd.to_datetime(row.get('date'), errors='coerce'),
                make=row.get('make', None),
                model=row.get('model', None),
                city=row.get('city', None),
                municipality=row.get('municipality', None),
                scraped_at=datetime.now(timezone.utc)
            )
            cars_to_insert.append(car)
            existing_cars.add(car_key)  # add to set so subsequent rows also avoid duplicates

        session.bulk_save_objects(cars_to_insert)
        session.commit()
        print(f"Inserted {len(cars_to_insert)} new cars into the database.")

    except Exception as e:
        session.rollback()
        print("Error inserting cars:", e)
    finally:
        print(f"Processed {len(df)} rows; {len(cars_to_insert)} new cars added.")
        session.close()
