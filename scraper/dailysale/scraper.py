from scrapingbee import ScrapingBeeClient
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

def get_products():
    """Scrape products from DailySale and return as list"""
    try:
        client = ScrapingBeeClient(api_key=os.environ.get('SCRAPINGBEE_API_KEY'))
        response = client.get('https://www.dailysale.co.zw/categories/tv-audio-video/all')
        
        if response.status_code != 200:
            raise Exception(f"Scraping failed with status {response.status_code}")

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
                continue

        return products
    except Exception as e:
        print(f"Error in DailySale scraper: {e}")
        return []
