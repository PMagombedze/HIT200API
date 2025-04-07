#!/bin/bash

# Start the product scraper scheduler in background
nohup python3 -u -m scraper.scheduler > scheduler.log 2>&1 &

echo "Product scraper scheduler started in background"
echo "Logs are being written to scheduler.log"
echo "To stop: pkill -f 'python3 -m scraper.scheduler'"