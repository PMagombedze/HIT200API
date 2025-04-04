from scrapingbee import ScrapingBeeClient
import json, os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

def get_products():
    """Scrape products from FirstPack and return as list"""
    try:
        client = ScrapingBeeClient(api_key=os.environ.get('SCRAPINGBEE_API_KEY'))
        response = client.get('https://www.firstpack.co.zw/category/INT')

        if response.status_code != 200:
            raise Exception(f"Failed to fetch the webpage: {response.status_code}")

        soup = BeautifulSoup(response.content, 'html.parser')
        products = []

        for product in soup.find_all('div', {'class': 'col-6 col-md-4 col-lg-3 mb-1 p-1'}):
            try:
                product_block = product.find('div', {'class': 'card p-0 m-0 border-0'})
                name = product_block.find('h5', {'class': 'card-title'}).text.strip()
                price = product_block.find('span', {'class': 'text-danger d-block fw-bolder text-end'}).text.strip()
                model = product_block.find('span', {'class': 'text-white bg-black d-block text-end'}).text.strip()
                brand = product_block.find('span', {'class': 'text-muted d-block text-end'}).text.strip()
                description = name  # Assuming description is not provided separately
                image = product_block.find('img', {'class': 'card-img-top mx-auto'})['src']

                products.append({
                    'name': name,
                    'price': price,
                    'model': model,
                    'brand': brand,
                    'description': description,
                    'url': image,
                    'store': 'firstpack'
                })
            except Exception as e:
                print(f"Error processing product: {e}")
                continue

        return products
    except Exception as e:
        print(f"Error in FirstPack scraper: {e}")
        return []
    