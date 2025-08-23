from bs4 import BeautifulSoup
import requests

url = 'https://www.pazar3.mk/oglasi/vozila/avtomobili'

page = requests.get(url)

soup = BeautifulSoup(page.content, 'lxml')

rows = soup.find_all('div', class_='row-listing')

cars = []
for row in rows:
    car = {}

    image = row.find('img', class_='ProductionImg')
    if image:
        url = image.get('data-src') or image.get('src')
        car['image_url'] = url
    else:
        print('No image found')

    title = row.find('a', class_='Link_vis')
    if title:
        car['title'] = title.text.strip()
        car['url'] = 'https://www.pazar3.mk' + title.get('href')
    else:
        print('No title found')

    price = row.find('p', class_='list-price')
    if price:
        car['price'] = price.text.strip()
        car['price'] = car['price'].replace('ЕУР', 'EUR').replace('МКД', 'MKD')
    else:
        print('No price found')

    bolds = row.find('div', class_='left-side').find_all('b')
    if len(bolds) >= 2:
        car['year'] = bolds[0].text.strip()
        car['mileage'] = bolds[1].text.strip()
    else:
        print('Year or mileage not found')

    additional_info = row.find('div', class_='title')
    date = additional_info.find('span')
    if date:
        car['date'] = date.text.strip()
    else:
        print('No date found')
    
    a_tags = additional_info.find_all('a')[1:5]
    texts = [a.text.strip() for a in a_tags]
    print(texts)
    car['make'] = texts[0] if len(texts) > 1 else None
    car['model'] = texts[1] if len(texts) > 2 else None
    car['city'] = texts[2] if len(texts) > 3 else None
    car['municipality'] = texts[3] if len(texts) > 4 else None

    cars.append(car)

for car in cars:
    print(f"Title       : {car.get('title')}")
    print(f"Price       : {car.get('price')}")
    print(f"Year        : {car.get('year')}")
    print(f"Mileage     : {car.get('mileage')}")
    print(f"Date        : {car.get('date')}")
    print(f"URL         : {car.get('url')}")
    print(f"Image URL   : {car.get('image_url')}")
    print(f"Make        : {car.get('make')}")
    print(f"Model       : {car.get('model')}")
    print(f"City        : {car.get('city')}")
    print(f"Municipality: {car.get('municipality')}")
    print('-' * 80)  # separator between cars