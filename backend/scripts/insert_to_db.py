import pandas as pd
from datetime import datetime, timezone
from app.db.session import SessionLocal  
from app.models import Car   
import numpy as np 

def insert_cleaned_to_db(df=None, csv_path=None):
    """
    Insert cleaned cars into the database.
    Either pass a DataFrame via `df` or a CSV path via `csv_path`.
    """
    if df is None and csv_path is not None:
        df = pd.read_csv(csv_path, encoding='utf-8-sig', keep_default_na=False)
    elif df is None and csv_path is None:
        raise ValueError("You must provide either a DataFrame or a CSV path")

    # Replace NaN with None for SQLAlchemy compatibility
    df = df.replace({np.nan: None})
    session = SessionLocal()
    cars_to_insert = []
    try:
        # Pre-fetch all existing URLs to avoid duplicates
        existing_urls = {url for (url,) in session.query(Car.url).all()}

        for _, row in df.iterrows():
            # Check for pandas.Na and convert to None
            year_value = row.get('year')
            price_value = row.get('price')
            mileage_value = row.get('mileage')
            if pd.isna(year_value):
                year_value = None
            if pd.isna(price_value):
                price_value = None
            if pd.isna(mileage_value):
                mileage_value = None

            url_value = row.get('url', None)
            if not url_value or url_value in existing_urls:
                continue
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

        session.bulk_save_objects(cars_to_insert)
        session.commit()
        print(f"Inserted {len(cars_to_insert)} new cars into the database.")

    except Exception as e:
        session.rollback()
        print("Error inserting cars:", e)
    finally:
        print(f"Processed {len(df)} rows; {len(cars_to_insert)} new cars added.")
        session.close()
