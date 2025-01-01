from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from auth.api import jwt_redis_blocklist
from models.db import User, db
import re

def validate_reference(reference):
    return bool(re.match(r'^MP\d{6}\.\d{4}\.K\d{5}$', reference))


payments = Blueprint('payments', __name__)

@payments.route('/payments', methods=['POST'])
@jwt_required()
def create_payment():
    # check redis blocklist
    jti = get_jwt()['jti']
    if jwt_redis_blocklist.get(jti):
        return jsonify({'message': 'Token has been revoked'}), 401
    
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    data = request.get_json()
    reference = data.get('reference')

    if not reference:
        return jsonify({'message': 'Reference is required'}), 400
    
    if not validate_reference(reference):
        return jsonify({'message': 'Invalid reference'}), 400
    
    if user.subscribed:
        return jsonify({'message': 'User is already subscribed'}), 400

    user.subscribed = True

    db.session.commit()
    return jsonify({'message': 'Payment successful'}), 201

@payments.route('/payments/cancel', methods=['POST'])
@jwt_required()
def cancel_subscription():
    # check redis blocklist
    jti = get_jwt()['jti']
    if jwt_redis_blocklist.get(jti):
        return jsonify({'message': 'Token has been revoked'}), 401
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if not user.subscribed:
        return jsonify({'message': 'User is not subscribed'}), 400
    user.subscribed = False
    db.session.commit()
    return jsonify({'message': 'Subscription cancelled'}), 200
