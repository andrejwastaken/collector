from datetime import datetime
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import json

base_url = 'https://www.pazar3.mk/oglasi/vozila/avtomobili/prodazba'

cars = []
page = 1
MAX_PAGES = 10
CRAWL_DELAY = 20  # seconds

while True:
    if page > MAX_PAGES:
        print(f"Reached MAX_PAGES ({MAX_PAGES}). Stopping.")
        break

    print(f'Scraping page {page}...')
    url = f"{base_url}?Page={page}" if page > 1 else base_url
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'lxml')
    rows = soup.find_all('div', class_='row-listing')

    if not rows:
        print('No more listings found.')
        break

    for row in rows:
        car = {}

        # Extract image URL
        image = row.find('img', class_='ProductionImg')
        if image:
            car["image_url"] = image.get("data-src") or image.get("src")
        else:
            car["image_url"] = None

        # Extract title and URL
        title = row.find('a', class_='Link_vis')
        if title:
            car["title"] = title.text.strip()
            car["url"] = "https://www.pazar3.mk" + title.get("href")
        else:
            car["title"] = None
            car["url"] = None

        # Extract price
        price = row.find('p', class_='list-price')
        if price:
            car["price"] = price.text.strip().replace("ЕУР", "EUR").replace("МКД", "MKD")
        else:
            car["price"] = None

        # Extract year and mileage
        bolds = row.find('div', class_='left-side').find_all('b')
        car["year"] = bolds[0].text.strip() if len(bolds) >= 1 else None
        car["mileage"] = bolds[1].text.strip() if len(bolds) >= 2 else None

        # Extract date, make, model, city, municipality
        additional_info = row.find('div', class_='title')
        if additional_info:
            date = additional_info.find('span')
            car["date"] = date.text.strip() if date else None
            
            a_tags = additional_info.find_all('a', recursive=False)
            if len(a_tags) >= 4 and a_tags[0].text.strip() == 'Автомобили':
                a_tags = a_tags[1:]
            else:
                a_tags = a_tags[2:]

            texts = [a.text.strip() for a in a_tags]
            car['make'] = texts[0] if len(texts) > 0 else None
            car['model'] = texts[1] if len(texts) > 1 else None
            car['city'] = texts[2] if len(texts) > 2 else None
            car['municipality'] = texts[3] if len(texts) > 3 else None
        else:
            car["date"] = car["make"] = car["model"] = car["city"] = car["municipality"] = None
        cars.append(car)
    page += 1
    print(f"Waiting {CRAWL_DELAY} seconds to be polite...")
    time.sleep(CRAWL_DELAY)

# First check if the CSV file with scraped data exists
try:
    df_existing = pd.read_csv('data/raw/cars.csv', encoding='utf-8-sig')
except FileNotFoundError:
    df_existing = pd.DataFrame()

df_new = pd.DataFrame(cars)
df_new['scraped_at'] = datetime.now()

# Combine existing and new data, remove duplicates based on 'url', keep the latest entry
df_combined = pd.concat([df_existing, df_new], ignore_index=True)
# Ensure scraped_at is datetime
df_combined['scraped_at'] = pd.to_datetime(df_combined['scraped_at'], errors='coerce')

df_combined.sort_values('scraped_at', ascending=False, inplace=True)
df_cleaned = df_combined.drop_duplicates(subset='url', keep='first')

# Save to CSV and JSON
df_cleaned.to_csv('data/raw/cars.csv', index=False, encoding='utf-8-sig')

with open('data/raw/cars.json', 'w', encoding='utf-8') as f:
    json.dump(cars, f, ensure_ascii=False, indent=4)

print(f"Scraping done. {len(cars)} cars saved to CSV and JSON with timestamp {datetime.now()}.")