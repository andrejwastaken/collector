import pandas as pd
from datetime import datetime, timedelta

# --- Helper functions ---
def parse_price(price_str):
    if not price_str or not isinstance(price_str, str):
        return None

    price_str = price_str.replace(" ", "").upper()

    try:
        if "EUR" in price_str:
            value = float(price_str.replace("EUR", ""))
            return value
        elif "MKD" in price_str:
            value = float(price_str.replace("MKD", ""))
            eur_value = value / 61.5  # adjust if exchange rate changes
            return round(eur_value, 2)
        else:
            # handle weird listings like "1" or unknown formats
            value = float(''.join(filter(str.isdigit, price_str)))
            if value > 1000:  # assume MKD if big number
                return round(value / 61.5, 2)
            return value
    except ValueError:
        return None

def parse_mileage(mileage_str):
    if not isinstance(mileage_str, str):
        return None

    parts = mileage_str.replace(' ', '').split('-')
    if len(parts) != 2:
        return None

    try:
        start = int(parts[0])
        end = int(parts[1])
    except ValueError:
        return None

    mileage_avg = (start + end) // 2

    if mileage_avg >= 0:
        return mileage_avg
    return None

MONTHS = {
    'јан.': 1, 'фев.': 2, 'мар.': 3, 'апр.': 4, 'мај.': 5, 'јун.': 6,
    'јул.': 7, 'авг.': 8, 'сеп.': 9, 'окт.': 10, 'ноем.': 11, 'дек.': 12
}

def parse_date(date_str):
    date_str = str(date_str).strip()
    now = datetime.now()
    
    if date_str.startswith('Денес'):
        time_part = date_str.split()[1]
        hour, minute = map(int, time_part.split(':'))
        return now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    elif date_str.startswith('Вчера'):
        time_part = date_str.split()[1]
        hour, minute = map(int, time_part.split(':'))
        yesterday = now - timedelta(days=1)
        return yesterday.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    else:
        parts = date_str.split()
        if len(parts) == 3:
            try:
                day = int(parts[0])
                month = MONTHS.get(parts[1], None)
                hour, minute = map(int, parts[2].split(':'))
                if month is None:
                    return None
                return datetime(now.year, month, day, hour, minute)
            except Exception:
                return None
    return None

# --- Main cleaning function ---
def clean_data(df: pd.DataFrame,
               output_csv='data/cleaned/cars_cleaned.csv',
               output_json='data/cleaned/cars_cleaned.json') -> pd.DataFrame:

    df_cleaned = df.copy()

    # Fill missing strings
    df_cleaned['image_url'] = df_cleaned['image_url'].fillna('no_image')
    df_cleaned['title'] = df_cleaned['title'].fillna('no_title')
    df_cleaned['url'] = df_cleaned['url'].fillna('no_url')
    df_cleaned['make'] = df_cleaned['make'].fillna('no_make')
    df_cleaned['model'] = df_cleaned['model'].fillna('no_model')
    df_cleaned['city'] = df_cleaned['city'].fillna('no_city')
    df_cleaned['municipality'] = df_cleaned['municipality'].fillna('no_municipality')

    # Parse numeric/date fields
    df_cleaned['price'] = df_cleaned['price'].apply(parse_price)
    df_cleaned['year'] = df_cleaned['year'].astype('Int64')
    df_cleaned['mileage'] = df_cleaned['mileage'].apply(parse_mileage)
    df_cleaned['date'] = df_cleaned['date'].apply(parse_date)

    # Save cleaned data
    df_cleaned.to_csv(output_csv, index=False, encoding='utf-8-sig')
    df_cleaned.to_json(output_json, orient='records', force_ascii=False, indent=4)

    print("Data cleaned and saved to CSV and JSON.")
    return df_cleaned
