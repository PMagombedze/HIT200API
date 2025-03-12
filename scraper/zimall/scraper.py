from scrapingbee import ScrapingBeeClient
import json, os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

client = ScrapingBeeClient(api_key=os.environ.get('SCRAPINGBEE_API_KEY'))
response = client.get('https://www.zimall.co.zw/shop/categories/4/electronics-appliances.html')

soup = BeautifulSoup(response.content, 'html.parser')
products = []

for product in soup.find_all('li', {'class': 'ajax_block_product'}):
    product_block = product.find('div', {'class': 'product-block'})
    name = product_block.find('h4', {'class': 'name'}).text.strip()
    price = product_block.find('span', {'itemprop': 'price'}).text.strip()
    model = product_block.find('meta', {'itemprop': 'Model'})['content']
    brand = product_block.find('meta', {'itemprop': 'Brand'})['content']
    description = product_block.find('div', {'class': 'product-desc'}).text.strip()
    image = product_block.find('img', {'class': 'replace-2x'})['src']

    products.append({
        'name': name,
        'price': price,
        'model': model,
        'brand': brand,
        'description': description,
        'url': image,
        'store': 'zimall'
    })

with open('electronics_zimall.json', 'w') as f:
    json.dump(products, f, indent=4)


client = ScrapingBeeClient(api_key=os.environ.get('SCRAPINGBEE_API_KEY'))
response = client.get('https://www.dailysale.co.zw/categories/tv-audio-video/all')

soup = BeautifulSoup(response.content, 'html.parser')
products = []

for product in soup.find_all('li', {'class': 'ajax_block_product'}):
    product_block = product.find('div', {'class': 'product-block'})
    name = product_block.find('h4', {'class': 'name'}).text.strip()
    price = product_block.find('span', {'itemprop': 'price'}).text.strip()
    model = product_block.find('meta', {'itemprop': 'Model'})['content']
    brand = product_block.find('meta', {'itemprop': 'Brand'})['content']
    description = product_block.find('div', {'class': 'product-desc'}).text.strip()
    image = product_block.find('img', {'class': 'replace-2x'})['src']

    products.append({
        'name': name,
        'price': price,
        'model': model,
        'brand': brand,
        'description': description,
        'url': image,
        'store': 'zimall'
    })

with open('tv_audio_video_json.json', 'w') as f:
    json.dump(products, f, indent=4)