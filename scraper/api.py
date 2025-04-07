from flask import Blueprint, request
import json
from flask import jsonify

products = Blueprint('products', __name__)

@products.route('/products', methods=['GET'])
def get_products():
    try:
        with open('/home/percy/Documents/HIT200API/scraper/products.json', 'r') as file:
            content = file.read()
            if not content.strip():
                return jsonify([])
            products_data = json.loads(content)
        return jsonify(products_data)
    except FileNotFoundError:
        return jsonify([])
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON data"}), 500

@products.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    try:
        with open('/home/percy/Documents/HIT200API/scraper/products.json', 'r') as file:
            products_data = json.load(file)
    except FileNotFoundError:
        products_data = []
    
    if isinstance(products_data, dict):
        if 'products' not in products_data:
            products_data['products'] = []
        products_data['products'].append(data)
    else:
        products_data.append(data)
        with open('/home/percy/Documents/HIT200API/scraper/products.json', 'w') as file:
            json.dump(products_data, file)
    return jsonify(data), 201