from scrapingbee import ScrapingBeeClient
import json, os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize ScrapingBee client
client = ScrapingBeeClient(api_key=os.environ.get('SCRAPINGBEE_API_KEY'))

def get_products():
    """Scrape products from TopDeals and return as list"""
    try:
        client = ScrapingBeeClient(api_key=os.environ.get('SCRAPINGBEE_API_KEY'))
        products = []

        # Loop through pages for both categories
        for category, pages in [('home-kitchen', 15), ('babies-moms', 3)]:
            for page in range(1, pages + 1):
                url = f'https://www.topdeals.co.zw/product-categories/{category}?page={page}'
                response = client.get(url)

                if response.status_code != 200:
                    raise Exception(f"Failed to fetch the webpage: {response.status_code}")

                # Parse the HTML content
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract product details
                for product in soup.find_all('div', {'class': 'ps-product'}):
                    try:
                        thumbnail = product.find('div', {'class': 'ps-product__thumbnail'})
                        container = product.find('div', {'class': 'ps-product__container'})

                        name = container.find('a', {'class': 'ps-product__title'}).text.strip()
                        price = container.find('p', {'class': 'ps-product__price'}).text.strip()
                        product_url = thumbnail.find('a')['href']
                        image = thumbnail.find('img')['src']

                        products.append({
                            'name': name,
                            'price': price,
                            'url': product_url,
                            'image': image,
                            'store': 'topdeals'
                        })
                    except Exception as e:
                        print(f"Error processing product: {e}")
                        continue

        return products
    except Exception as e:
        print(f"Error in TopDeals scraper: {e}")
        return []
