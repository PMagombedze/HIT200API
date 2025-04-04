from scrapingbee import ScrapingBeeClient
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = ScrapingBeeClient(api_key=os.environ.get('SCRAPINGBEE_API_KEY'))
response = client.get('https://raines.africa/product-category/televisions/')

def get_products():
    """Scrape products from Raines Africa and return as list"""
    try:
        client = ScrapingBeeClient(api_key=os.environ.get('SCRAPINGBEE_API_KEY'))
        response = client.get('https://raines.africa/product-category/televisions/')

        if response.status_code != 200:
            raise Exception(f"Failed to fetch the webpage: {response.status_code}")

        soup = BeautifulSoup(response.content, 'html.parser')
        products = []

        for product in soup.find_all('div', {'class': 'product-small col has-hover'}):
            try:
                product_inner = product.find('div', {'class': 'col-inner'})
                name = product_inner.find('p', {'class': 'name product-title woocommerce-loop-product__title'}).text.strip()
                price = product_inner.find('span', {'class': 'woocommerce-Price-amount amount'}).text.strip()
                category = product_inner.find('p', {'class': 'category uppercase is-smaller no-text-overflow product-cat op-7'}).text.strip()
                url = product_inner.find('a', {'class': 'woocommerce-LoopProduct-link woocommerce-loop-product__link'})['href']
                image = product_inner.find('img', {'class': 'attachment-woocommerce_thumbnail'})['src']

                products.append({
                    'name': name,
                    'price': price,
                    'category': category,
                    'url': url,
                    'image': image,
                    'store': 'raines_africa'
                })
            except Exception as e:
                print(f"Error processing product: {e}")
                continue

        return products
    except Exception as e:
        print(f"Error in Raines Africa scraper: {e}")
        return []