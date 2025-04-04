import os
from scrapingbee import ScrapingBeeClient
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

def get_products():
    """Scrape products from Everything Zimbabwe and return as list"""
    try:
        client = ScrapingBeeClient(api_key=os.environ.get('SCRAPINGBEE_API_KEY'))
        response = client.get('https://everythingzimbabwean.com/category/electronic-goods/')
        
        if response.status_code != 200:
            raise Exception(f"Scraping failed with status {response.status_code}")

        soup = BeautifulSoup(response.content, 'html.parser')
        products = []

        for product in soup.find_all('li', {'class': 'product-tile '}):
            try:
                product_link = product.find('a', {'class': 'product-link'})['href']
                product_image = product.find('img', {'class': 'attachment-medium'})['src']
                product_name = product.find('div', {'class': 'name'}).text.strip()
                product_price = product.find('div', {'class': 'price'}).text.strip()
                seller_info = product.find('div', {'class': 'seller-html'}).text.strip()

                products.append({
                    'name': product_name,
                    'price': product_price,
                    'seller': seller_info,
                    'url': product_link,
                    'image': product_image,
                    'store': 'everythingzimbabwean'
                })
            except Exception as e:
                print(f"Error processing product: {e}")
                continue

        return products
    except Exception as e:
        print(f"Error in Everything Zimbabwe scraper: {e}")
        return []