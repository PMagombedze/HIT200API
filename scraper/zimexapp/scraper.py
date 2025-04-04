from scrapingbee import ScrapingBeeClient
import json, os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# filepath: c:/Users/takue/Documents/GitHub/HIT200API/scraper/zimexapp/scraper.py

load_dotenv()
def get_products():
    """Scrape products from ZimexApp and return as list"""
    try:
        client = ScrapingBeeClient(api_key=os.environ.get('SCRAPINGBEE_API_KEY'))
        response = client.get('https://zimexapp.co.zw/cellphone')

        if response.status_code != 200:
            raise Exception(f"Failed to fetch the webpage: {response.status_code}")

        soup = BeautifulSoup(response.content, 'html.parser')
        products = []

        for product in soup.find_all('div', {'class': 'span3 item'}):
            try:
                dealbrick = product.find('div', {'class': 'dealbrick'})
                name = dealbrick.find('a', {'class': 'titleclick'}).text.strip()
                price = dealbrick.find('li', {'class': 'price'}).text.strip().split(' ')[0]
                description = dealbrick.find('li', {'class': 'hide cat-deal-data'})['data-descp']
                image = dealbrick.find('img', {'class': 'dealpic'})['src']
                dealer_element = dealbrick.find('li', {'class': 'padded'})
                dealer = dealer_element.find('a', {'class': 'btn-dealerprofile'}).text.strip() if dealer_element and dealer_element.find('a', {'class': 'btn-dealerprofile'}) else 'Unknown Dealer'
                product_url = dealbrick.find('a', {'class': 'titleclick'})['href']

                products.append({
                    'name': name,
                    'price': price,
                    'description': description,
                    'image': f"https://zimexapp.co.zw/{image}",
                    'dealer': dealer,
                    'url': f"https://zimexapp.co.zw/{product_url}",
                    'store': 'zimexapp'
                })
            except Exception as e:
                print(f"Error processing product: {e}")
                continue

        return products
    except Exception as e:
        print(f"Error in ZimexApp scraper: {e}")
        return []
