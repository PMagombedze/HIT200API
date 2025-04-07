from scrapingbee import ScrapingBeeClient
import json, os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_products():
    # Initialize ScrapingBee client
    client = ScrapingBeeClient(api_key=os.environ.get('SCRAPINGBEE_API_KEY'))

    products = []

    # Loop through pages 1 to 15 for home-kitchen
    for page in range(1, 16):
        url = f'https://www.topdeals.co.zw/product-categories/home-kitchen?page={page}'
        response = client.get(url)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract product details
        for product in soup.find_all('div', {'class': 'ps-product'}):
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

    # Loop through pages 1 to 3 for babies-moms
    for page in range(1, 4):
        url = f'https://www.topdeals.co.zw/product-categories/babies-moms?page={page}'
        response = client.get(url)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract product details
        for product in soup.find_all('div', {'class': 'ps-product'}):
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

    return products

print(get_products())