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
        # keep_default_na=False is important to read empty strings as ''
        df = pd.read_csv(csv_path, encoding='utf-8-sig', keep_default_na=False)
    elif df is None and csv_path is None:
        raise ValueError("You must provide either a DataFrame or a CSV path")

    # Replace empty strings with None across the entire DataFrame
    df = df.replace({'': None})
    # Replace NaNs with None for SQLAlchemy
    df = df.replace({np.nan: None})

    def clean_date(val):
        if pd.isna(val) or val is None:
            return None
        try:
            date_val = pd.to_datetime(val, errors='coerce')
            if pd.isna(date_val):
                return None
            return date_val
        except Exception:
            return None

    df['date'] = df['date'].apply(clean_date)
    # This line might be redundant now, but it's good practice apparently
    df['date'] = df['date'].replace({pd.NaT: None})

    session = SessionLocal()
    cars_to_insert = []

    try:
        # Pre-fetch existing cars as tuples of (title, mileage, year)
        existing_cars = set(
            session.query(Car.title, Car.mileage_km, Car.year).all()
        )

        for _, row in df.iterrows():
            year_raw = row.get('year')
            mileage_raw = row.get('mileage')

            year_value = None
            if year_raw is not None:
                try:
                    year_value = int(year_raw)
                except (ValueError, TypeError):
                    year_value = None

            mileage_value = None
            if mileage_raw is not None:
                try:
                    mileage_value = int(mileage_raw)
                except (ValueError, TypeError):
                    mileage_value = None

            price_raw = row.get('price')
            price_value = None
            if price_raw is not None:
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
                date_posted=row['date'],
                make=row.get('make', None),
                model=row.get('model', None),
                city=row.get('city', None),
                municipality=row.get('municipality', None),
                scraped_at=datetime.now(timezone.utc)
            )
            cars_to_insert.append(car)
            existing_cars.add(car_key)

        session.bulk_save_objects(cars_to_insert)
        session.commit()
        print(f"Inserted {len(cars_to_insert)} new cars into the database.")

    except Exception as e:
        session.rollback()
        print("Error inserting cars:", e)
    finally:
        print(f"Processed {len(df)} rows; {len(cars_to_insert)} new cars added.")
        session.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python insert_cars.py <csv_file>")
        sys.exit(1)

    csv_file = sys.argv[1]
    insert_cleaned_to_db(csv_path=csv_file)