from flask import jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from auth.api import jwt_redis_blocklist
from models.db import Product

products = Blueprint('products', __name__)

@products.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    if jwt_redis_blocklist.get(get_jwt()['jti']):
        return jsonify({'message': 'Token revoked'}), 401
    user = get_jwt_identity()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    products = Product.query.all()
    return jsonify({'products': [product.to_dict() for product in products]}), 200