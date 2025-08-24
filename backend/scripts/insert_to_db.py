import pandas as pd
from datetime import datetime, timezone
from app.db.session import SessionLocal  
from app.models import Car   

def insert_cleaned_to_db(df=None, csv_path=None):
    """
    Insert cleaned cars into the database.
    Either pass a DataFrame via `df` or a CSV path via `csv_path`.
    """
    print(1)
    if df is None and csv_path is not None:
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
    elif df is None and csv_path is None:
        raise ValueError("You must provide either a DataFrame or a CSV path")

    session = SessionLocal()
    cars_to_insert = []
    try:
        # Pre-fetch all existing URLs to avoid duplicates
        existing_urls = {url for (url,) in session.query(Car.url).all()}

        for _, row in df.iterrows():
            # Check for pandas.NA and convert to None
            year_value = row.get('year', None)
            if pd.isna(year_value):
                year_value = None
            url_value = row.get('url', None)
            if not url_value or url_value in existing_urls:
                continue
            car = Car(
                image_url=row.get('image_url', None),
                title=row.get('title', None),
                url=row.get('url', None),
                price_num=row.get('price', None),
                year=year_value,
                mileage_km=row.get('mileage', None),
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
