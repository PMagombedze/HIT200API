from scrapingbee import ScrapingBeeClient
import json, os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

client = ScrapingBeeClient(api_key=os.environ.get('SCRAPINGBEE_API_KEY'))
response = client.get('https://www.zimall.co.zw/shop/categories/4/electronics-appliances.html')

soup = BeautifulSoup(response.content, 'html.parser')
products = []

for product in soup.find_all('li', {'class': 'ajax_block_product'}):
    product_block = product.find('div', {'class': 'product-block'})
    name = product_block.find('h4', {'class': 'name'}).text.strip()
    price = product_block.find('span', {'itemprop': 'price'}).text.strip()
    model = product_block.find('meta', {'itemprop': 'Model'})['content']
    brand = product_block.find('meta', {'itemprop': 'Brand'})['content']
    description = product_block.find('div', {'class': 'product-desc'}).text.strip()
    image = product_block.find('img', {'class': 'replace-2x'})['src']

    products.append({
        'name': name,
        'price': price,
        'model': model,
        'brand': brand,
        'description': description,
        'url': image,
        'store': 'zimall'
    })

with open('electronics_zimall.json', 'w') as f:
    json.dump(products, f, indent=4)
import os
import json
from bs4 import BeautifulSoup
import requests

# Function to scrape computer products from Zimshops
def scrape_zimshops_computers():
    # Target URL for computer products
    url = 'https://www.zim-shops.com/catergory2.php?catergory=Electricals'
    
    print(f"Fetching content from {url}...")
    
    # Using a simple request first - can be replaced with ScrapingBee if needed
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch content: {response.status_code}")
            
        # Parse the content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # List to store product data
        products = []
        
        # Find all product containers - based on the HTML structure provided
        print("Extracting product data...")
        product_containers = soup.find_all('div', {'class': 'products'})
        
        for container in product_containers:
            # Extract product name
            name_element = container.find('h4', {'class': 'product-name'})
            name = name_element.text.strip() if name_element else "Name not found"
            
            # Extract product price
            price_element = container.find('p', {'class': 'price'})
            if price_element:
                # Extract the price value, removing "Price : " prefix
                price_text = price_element.text.strip()
                price = price_text.replace('Price : ', '').strip()
            else:
                price = "Price not found"
            
            # Extract product image URL
            image_element = container.find('img')
            image = None
            if image_element:
                # Get the image source
                image_src = image_element.get('src')
                # Convert relative paths to absolute URLs
                if image_src and not image_src.startswith('http'):
                    image = f"https://www.zim-shops.com/{image_src}"
                else:
                    image = image_src or "Image not found"
            else:
                image = "Image not found"
            
            # Extract product URL
            url_element = container.find('a', {'class': 'product'})
            product_url = None
            if url_element:
                href = url_element.get('href')
                if href and not href.startswith('http'):
                    product_url = f"https://www.zim-shops.com/{href}"
                else:
                    product_url = href or "URL not found"
            else:
                product_url = "URL not found"
            
            # Extract product ID
            prod_id_element = container.find('input', {'name': 'prod_id'})
            prod_id = prod_id_element.get('value') if prod_id_element else "ID not found"
            
            # Append the product data to the list
            products.append({
                'name': name,
                'price': price,
                'image': image,
                'url': product_url,
                'id': prod_id,
                'category': 'Computers',
                'store': 'zimshops.com'
            })
        
        # Save the scraped data to a JSON file
        output_file = 'zimshops_computer_products.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=4, ensure_ascii=False)
        
        print(f"Scraped {len(products)} products. Data saved to {output_file}")
        return products
    
    except Exception as e:
        print(f"Error scraping Zimshops: {e}")
        return []

# Optional: Using ScrapingBee
def scrape_with_scrapingbee():
    from scrapingbee import ScrapingBeeClient
    
    # Initialize ScrapingBee client
    api_key = os.environ.get('SCRAPINGBEE_API_KEY')
    if not api_key:
        raise ValueError("SCRAPINGBEE_API_KEY environment variable is not set")
    
    client = ScrapingBeeClient(api_key=api_key)
    
    # Target URL for computer products
    url = 'https://www.zim-shops.com/catergory2.php?catergory=Computers'
    
    print(f"Fetching content from {url} using ScrapingBee...")
    response = client.get(
        url,
        params={
            'render_js': 'false',  # Set to true if the site requires JavaScript
            'premium_proxy': 'true'  # Use premium proxies for better reliability
        }
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch content: {response.status_code}")
    
    # Continue with BeautifulSoup parsing as in the main function
    # ...

# Run the scraper
if __name__ == "__main__":
    products = scrape_zimshops_computers()
    print(f"Total products scraped: {len(products)}")
