import os
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

base_url = "https://innovative.co.zw/shop/?wpf=wpf_6683132d4a741&wpf_cols=5&wpf_cat=accessories%2Caudio%2Ccameras%2Ccontrol%2Cdesktop%2Cdisplay%2Celectric-accessories%2Cgaming%2Claptops%2Cmemory%2Cmonitors%2Cnetworking%2Cprinters%2Cprojectors%2Cram%2Cscanners%2Csmartphones%2Ctablets%2Ctvs"
products = []

for page in range(1, 28):  # Loop through all pages
    url = f"{base_url}&product-page={page}"
    print(f"Fetching content from {url}...")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    for product in soup.find_all('li', {'class': 'product'}):
        name = product.find('h2', {'class': 'woocommerce-loop-product__title'}).text.strip()
        price = product.find('span', {'class': 'woocommerce-Price-amount'}).text.strip()
        image = product.find('img', {'class': 'attachment-woocommerce_thumbnail'})['src']
        link = product.find('a', {'class': 'woocommerce-LoopProduct-link'})['href']

        products.append({
            'name': name,
            'price': price,
            'image': image,
            'url': link,
            'store': 'innovative technologies'
        })

with open('electronics_innovative_technologies.json', 'w') as f:
    json.dump(products, f, indent=4)

print("Scraping completed. Data saved to products_innovative.json.")