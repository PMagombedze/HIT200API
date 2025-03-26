from scrapingbee import ScrapingBeeClient
import json, os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize ScrapingBee client
client = ScrapingBeeClient(api_key=os.environ.get('SCRAPINGBEE_API_KEY'))

# URL to scrape
response = client.get('https://www.topdeals.co.zw/product-categories/home-kitchen')
response = client.get('https://www.topdeals.co.zw/product-categories/babies-moms')

# Parse the HTML content
soup = BeautifulSoup(response.content, 'html.parser')
products = []

# Loop through pages 1 to 15
products = []
for page in range(1, 16):
    url = f'https://www.topdeals.co.zw/product-categories/home-kitchen?page={page}'
    response = client.get(url)

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

# Save the scraped data to a JSON file
with open('electronics_topdeals.json', 'w') as f:
    json.dump(products, f, indent=4)

print(f"Scraped {len(products)} products. Data saved to electronics_topdeals.json")
