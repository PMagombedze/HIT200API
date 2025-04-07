from scrapingbee import ScrapingBeeClient
import json, os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

def get_products():
    client = ScrapingBeeClient(api_key=os.environ.get('SCRAPINGBEE_API_KEY'))
    response = client.get('https://www.dailysale.co.zw/categories/tv-audio-video/all')

    soup = BeautifulSoup(response.content, 'html.parser')
    products = []

    for product in soup.find_all('a', {'class': 'product-item'}):
        try:
            name = product.find('p', {'class': 'product-name'}).text.strip()
            price = product.find('p', {'class': 'product-price'}).text.strip()
            image = product.find('img')['src']
            url = 'https://www.dailysale.co.zw' + product['href']
            category = 'TV, Audio & Video'
            
            products.append({
                'name': name,
                'price': price,
                'image': image,
                'url': url,
                'category': category,
                'store': 'dailysale'
            })
        except Exception as e:
            print(f"Error processing product: {e}")

    with open('dailysale.json', 'w') as f:
        json.dump(products, f, indent=4)

    return products

print(get_products())