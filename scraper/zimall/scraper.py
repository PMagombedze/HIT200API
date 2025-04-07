from scrapingbee import ScrapingBeeClient
import json, os, logging, requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def get_products():
    url = 'https://www.zimall.co.zw/shop/categories/4/electronics-appliances.html'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.zimall.co.zw/'
    }
    
    # First try with ScrapingBee
    try:
        api_key = os.environ.get('SCRAPINGBEE_API_KEY')
        if api_key:
            client = ScrapingBeeClient(api_key=api_key)
            response = client.get(url)
            logger.info(f"ScrapingBee response status: {response.status_code}")
            if response.status_code == 200:
                return parse_products(response.content)
            logger.warning("ScrapingBee failed, falling back to direct request")
    except Exception as e:
        logger.warning(f"ScrapingBee error: {str(e)}")
    
    # Fall back to direct request
    try:
        response = requests.get(url, headers=headers, timeout=10)
        logger.info(f"Direct request status: {response.status_code}")
        if response.status_code == 200:
            return parse_products(response.content)
        logger.error(f"Direct request failed. Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Direct request error: {str(e)}")
    
    return []

def parse_products(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        product_elements = soup.find_all('li', {'class': 'ajax_block_product'})
        
        logger.info(f"Found {len(product_elements)} product elements")
        
        for product in product_elements:
            try:
                product_block = product.find('div', {'class': 'product-block'})
                if not product_block:
                    continue
                    
                name_elem = product_block.find('h4', {'class': 'name'})
                price_elem = product_block.find('span', {'itemprop': 'price'})
                model_elem = product_block.find('meta', {'itemprop': 'Model'})
                brand_elem = product_block.find('meta', {'itemprop': 'Brand'})
                desc_elem = product_block.find('div', {'class': 'product-desc'})
                img_elem = product_block.find('img', {'class': 'replace-2x'})

                products.append({
                    'name': name_elem.text.strip() if name_elem else 'N/A',
                    'price': price_elem.text.strip() if price_elem else 'N/A',
                    'model': model_elem['content'] if model_elem else 'N/A',
                    'brand': brand_elem['content'] if brand_elem else 'N/A',
                    'description': desc_elem.text.strip() if desc_elem else 'N/A',
                    'url': img_elem['src'] if img_elem else 'N/A',
                    'store': 'zimall'
                })
            except Exception as e:
                logger.error(f"Error parsing product: {str(e)}")
                continue

        return products
    except Exception as e:
        logger.error(f"Error parsing HTML: {str(e)}")
        return []
