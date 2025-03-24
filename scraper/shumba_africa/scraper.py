from scrapingbee import ScrapingBeeClient
import json, os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

client = ScrapingBeeClient(api_key=os.environ.get('SCRAPINGBEE_API_KEY'))
response = client.get('https://www.shumba.africa/store/?_sort=_regular_price_asc&_categories=electronics-computers')

soup = BeautifulSoup(response.content, 'html.parser')
products = []

for product in soup.find_all('article', {'class': 'wpgb-card'}):
    name = product.find('h3', {'class': 'wpgb-block-7'}).text.strip()
    price = product.find('div', {'class': 'wpgb-block-5'}).text.strip()
    url = product.find('a', {'class': 'wpgb-card-layer-link'})['href']
    image = product.find('div', {'class': 'wpgb-card-media-thumbnail'}).find('a')['href']
    product_id = product.find('a', {'class': 'add_to_cart_button'})['data-product_id']

    products.append({
        'name': name,
        'price': price,
        'url': url,
        'image': image,
        'id': product_id,
        'store': 'shumba.africa'
    })

with open('electronics_shumba_africa.json', 'w') as f:
    json.dump(products, f, indent=4)