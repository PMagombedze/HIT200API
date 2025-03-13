from scrapingbee import ScrapingBeeClient
import json, os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

client = ScrapingBeeClient(api_key=os.environ.get('SCRAPINGBEE_API_KEY'))
response = client.get('https://www.ubuy.co.zw/en/category/electronics-10171')

soup = BeautifulSoup(response.content, 'html.parser')
products = []

for product in soup.find_all('div', {'class': 'col-lg-3 col-md-4 col-sm-6 col-12 p-0 listing-product'}):
    try:
        product_card = product.find('div', {'class': 'product-card'})
        name = product_card.find('input', {'name': 'title'})['value'].strip()
        price = product_card.find('p', {'class': 'product-price'}).text.strip().split()[1]
        model = product_card.find('input', {'name': 'parent_sku'})['value']
        brand = product_card.find('a', {'class': 'goos-tag-product brand'}).text.strip()
        description = product_card.find('h3', {'class': 'product-title'}).text.strip()
        image = product_card.find('img', {'class': 'errorimg_ubuy_B07M942LN9'})['src']

        products.append({
            'name': name,
            'price': price,
            'model': model,
            'brand': brand,
            'description': description,
            'url': image,
            'store': 'ubuy'
        })
    except Exception as e:
        print(f"Error processing product: {e}")

with open('ubuy.json', 'w') as f:
    json.dump(products, f, indent=4)