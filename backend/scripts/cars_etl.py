from .scraper import scrape_cars       
from .cleaner import clean_data        
from .insert_to_db import insert_cleaned_to_db  

def main():
    print("Starting scraping...")
    raw_df = scrape_cars()
    print(f"Scraped {len(raw_df)} cars.")

    print("Cleaning data...")
    cleaned_df = clean_data(raw_df)
    print(f"Cleaned data contains {len(cleaned_df)} cars.")

    print("Inserting into database...")
    insert_cleaned_to_db(cleaned_df, csv_path='data/cleaned/cars.csv')
    print("Pipeline finished successfully!")

if __name__ == "__main__":
    main()
