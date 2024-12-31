from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from auth.api import jwt_redis_blocklist
import stripe
import os


stripe_keys = {
    "secret_key": os.environ["STRIPE_SECRET_KEY"],
    "publishable_key": os.environ["STRIPE_PUBLISHABLE_KEY"],
}

stripe.api_key = stripe_keys["secret_key"]


payments = Blueprint('payments', __name__)

@payments.route('/payments', methods=['POST'])
@jwt_required()
def process_payment():
    if jwt_redis_blocklist.get(get_jwt()['jti']):
        return jsonify({'message': 'Token revoked'}), 401

    current_user_id = get_jwt_identity()
    if not current_user_id:
        return jsonify({'message': 'User not found'}), 404
