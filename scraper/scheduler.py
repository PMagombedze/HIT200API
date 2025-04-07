import schedule
import time
import requests
from dotenv import load_dotenv
from datetime import datetime

# Import all scraper modules
from scraper.dailysale.scraper import get_products as dailysale_products
from scraper.everything_zimbabwe.scraper import get_products as everything_zimbabwe_products
from scraper.firstpack.scraper import get_products as firstpack_products
from scraper.fusertech.scraper import get_products as fusertech_products
from scraper.raines_africa.scraper import get_products as raines_africa_products
from scraper.shumba_africa.scraper import get_products as shumba_africa_products
from scraper.topdeals.scraper import get_products as topdeals_products
from scraper.ubuy.scraper import get_products as ubuy_products
from scraper.zimall.scraper import get_products as zimall_products
from scraper.zimexapp.scraper import get_products as zimexapp_products

load_dotenv()

def run_scrapers():
    """Run all scrapers and post results to API"""
    print(f"\n[{datetime.now()}] Running scrapers...")
    try:
        # List of all scraper functions
        scrapers = [
            dailysale_products,
            everything_zimbabwe_products,
            firstpack_products,
            fusertech_products,
            raines_africa_products,
            shumba_africa_products,
            topdeals_products,
            ubuy_products,
            zimall_products,
            zimexapp_products
        ]

        # Run all scrapers with error handling
        seen_products = set()
        for scraper in scrapers:
            print(f"Running {scraper.__module__}...")
            try:
                products = scraper()
                if products:
                    # Filter out duplicates based on product URL
                    unique_products = []
                    for product in products:
                        if product['url'] not in seen_products:
                            seen_products.add(product['url'])
                            unique_products.append(product)
                    
                    # Post unique products to API immediately
                    try:
                        response = requests.post("http://localhost:5000/api/products", json=unique_products)
                        if response.status_code == 200:
                            print(f"Successfully posted {len(unique_products)} products from {scraper.__module__} to API")
                        else:
                            print(f"Failed to post products from {scraper.__module__} to API. Status code: {response.status_code}")
                    except Exception as e:
                        print(f"Error posting products from {scraper.__module__} to API: {e}")
                    print(f"Collected {len(unique_products)} products from {scraper.__module__}")
            except Exception as e:
                print(f"Error in {scraper.__module__}: {e}")
                continue
    except Exception as e:
        print(f"Error in run_scrapers: {e}")

def main():
    # Schedule to run every 15 minutes
    schedule.every(15).minutes.do(run_scrapers)

    print("Starting product scraper scheduler...")
    print(f"Will run every 15 minutes, next run at {datetime.now()}")

    # Run immediately first time
    run_scrapers()

    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()