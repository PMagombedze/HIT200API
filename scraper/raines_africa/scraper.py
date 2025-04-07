from scrapingbee import ScrapingBeeClient
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import json

load_dotenv()

def get_products():
    try:
        client = ScrapingBeeClient(api_key=os.environ.get('SCRAPINGBEE_API_KEY'))
        response = client.get('https://raines.africa/product-category/televisions/')
        
        if response.status_code != 200:
            print(f"Failed to fetch page: {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        products = []

        product_grid = soup.find_all('div', {'class': 'product-small col has-hover'})
        if not product_grid:
            print("No products found - website structure may have changed")
            return []

        for product in product_grid:
            try:
                product_inner = product.find('div', {'class': 'col-inner'})
                if not product_inner:
                    continue

                name = product_inner.find('p', {'class': 'name product-title woocommerce-loop-product__title'})
                price = product_inner.find('span', {'class': 'woocommerce-Price-amount amount'})
                category = product_inner.find('p', {'class': 'category uppercase is-smaller no-text-overflow product-cat op-7'})
                url = product_inner.find('a', {'class': 'woocommerce-LoopProduct-link woocommerce-loop-product__link'})
                image = product_inner.find('img', {'class': 'attachment-woocommerce_thumbnail'})

                if not all([name, price, category, url, image]):
                    continue

                products.append({
                    'name': name.text.strip(),
                    'price': price.text.strip(),
                    'category': category.text.strip(),
                    'url': url['href'],
                    'image': image['src'],
                    'store': 'raines_africa'
                })
            except Exception as e:
                print(f"Error processing product: {e}")
                continue

    except Exception as e:
        print(f"Error in raines_africa scraper: {e}")
        return []


    return products

print(get_products())