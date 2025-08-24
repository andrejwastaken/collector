from datetime import datetime
from bs4 import BeautifulSoup
import requests
import pandas as pd
import json
import time
import os
BASE_URL = 'https://www.pazar3.mk/oglasi/vozila/avtomobili/prodazba'
MAX_PAGES = 20
CRAWL_DELAY = 20  # seconds

def scrape_cars(max_pages=MAX_PAGES, crawl_delay=CRAWL_DELAY):
    cars = []
    page = 1

    while True:
        print(f'Scraping page {page}...')
        url = f"{BASE_URL}?Page={page}" if page > 1 else BASE_URL
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
            car["image_url"] = image.get("data-src") or image.get("src") if image else None

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
            car["price"] = price.text.strip().replace("ЕУР", "EUR").replace("МКД", "MKD") if price else None

            # Extract year and mileage
            divs = row.find('div', class_='left-side').find_all('div')
            year, mileage = None, None

            for div in divs:
                text = div.get_text(strip=True)
                b_tag = div.find('b')
                if not b_tag:
                    continue
                value = b_tag.text.strip()
                if 'Година' in text:
                    try:
                        year = int(value)
                    except (ValueError, TypeError):
                        year = None
                elif 'Километража' in text:
                    if value and '-' in value:
                        parts = value.split('-')
                        try:
                            numbers = [float(p.replace(" ", "").strip()) for p in parts]
                            mileage = int(round(sum(numbers) / len(numbers)))
                        except ValueError:
                            mileage = None
                    else:
                        try:
                            mileage = float(value)
                        except ValueError:
                            mileage = None
            car["year"] = year
            car["mileage"] = mileage

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
                if len(texts) > 3:
                    car['municipality'] = texts[3] if texts[3] != 'Скопје' else None
                else:
                    car['municipality'] = None
            else:
                car["date"] = car["make"] = car["model"] = car["city"] = car["municipality"] = None

            cars.append(car)
        page += 1
        print(f"Waiting {crawl_delay} seconds to be polite...")
        if page > 2:
            print(f"Reached MAX_PAGES ({max_pages}). Stopping.")
            break
        time.sleep(crawl_delay)

    os.makedirs("data", exist_ok=True)
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/cleaned", exist_ok=True)
    df_existing = pd.read_csv('data/raw/cars.csv', encoding='utf-8-sig') if pd.io.common.file_exists('data/raw/cars.csv') else pd.DataFrame()
    df_new = pd.DataFrame(cars)
    df_new['scraped_at'] = datetime.now()

    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    df_combined['scraped_at'] = pd.to_datetime(df_combined['scraped_at'], errors='coerce')
    df_combined.sort_values('scraped_at', ascending=False, inplace=True)
    df_cleaned = df_combined.drop_duplicates(subset='url', keep='first')
    df_cleaned.to_csv('data/raw/cars.csv', index=False, encoding='utf-8-sig')

    with open('data/raw/cars.json', 'w', encoding='utf-8') as f:
        json.dump(cars, f, ensure_ascii=False, indent=4)

    print(f"Scraping done. {len(cars)} cars saved to CSV and JSON at {datetime.now()}.")

    return df_cleaned  # return dataframe so it can be used by other scripts

if __name__ == "__main__":
    scrape_cars()
