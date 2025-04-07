from scrapingbee import ScrapingBeeClient
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Initialize ScrapingBee client
client = ScrapingBeeClient(api_key=os.getenv("SCRAPINGBEE_API_KEY"))

# Base URL for scraping
base_url = "https://fusertech.co.zw/product-category/laptops/"
products = []

def get_products():
    # Loop through pages
    for page in range(1, 6):
        url = base_url if page == 1 else f"{base_url}page/{page}/"
        url += "?per_page=24"  # Add per_page parameter to each URL
        
        response = client.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Find product grid
        product_grid = soup.find("div", class_="products")
        if not product_grid:
            continue

        # Extract product details
        for item in product_grid.find_all("div", class_="product-grid-item"):
            title = item.find("h3", class_="wd-entities-title").text.strip()
            price = item.find("span", class_="woocommerce-Price-amount").text.strip()
            category = item.find("div", class_="wd-product-cats").text.strip()
            image = item.find("img", class_="attachment-woocommerce_thumbnail")["src"]
            link = item.find("a", class_="product-image-link")["href"]

            # Create individual product object
            product = {
                "name": title,
                "price": price,
                "category": category,
                "url": image,
                "link": link,
                "store": "fusertech"
            }
            
            products.append(product)
    
    # Return the products as direct JSON objects, not wrapped in a list
    return products

print(get_products())