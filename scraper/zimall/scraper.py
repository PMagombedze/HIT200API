import os
import json
from bs4 import BeautifulSoup
from scrapingbee import ScrapingBeeClient

# Initialize ScrapingBee client
client = ScrapingBeeClient(api_key=os.environ.get('SCRAPINGBEE_API_KEY'))

# Fetch the page content
response = client.get('https://www.dailysale.co.zw/categories/tv-audio-video/all')
soup = BeautifulSoup(response.content, 'html.parser')

# List to store product data
products = []

# Find all product containers
product_containers = soup.find_all('div', {'class': 'w-full'})

for container in product_containers:
    # Extract product name
    name = container.find('p', {'class': 'text-xs text-black line-clamp-2'}).text.strip()
    
    # Extract product price
    price = container.find('p', {'class': 'text-xs text-center sm:text-sm font-semibold text-[#CD0F0F]'}).text.strip()
    
    # Extract product image URL
    image = container.find('img')['src']
    
    # Extract product description (if available)
    description = container.find('p', {'class': 'text-xs text-black line-clamp-2'}).text.strip()
    
    # Extract product rating (if available)
    rating_element = container.find('span', {'class': 'text-[#707072]'})
    rating = rating_element.text.strip() if rating_element else "No rating"
    
    # Extract product discount (if available)
    discount_element = container.find('div', {'class': 'bg-primary'})
    discount = discount_element.text.strip() if discount_element else "No discount"
    
    # Append the product data to the list
    products.append({
        'name': name,
        'price': price,
        'image': image,
        'description': description,
        'rating': rating,
        'discount': discount,
        'store': 'dailysale'
    })

# Save the scraped data to a JSON file
with open('tv_audio_video.json', 'w') as f:
    json.dump(products, f, indent=4)

print(f"Scraped {len(products)} products.")