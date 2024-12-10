from models.db import UserProductVisit, db
from flask import jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from auth.api import jwt_redis_blocklist

recommendations = Blueprint('recommendations', __name__)

@recommendations.route('/products/<product_id>/visit', methods=['POST'])
@jwt_required()
def track_product_visit(product_id):
    current_user_id = get_jwt_identity()
    visit = UserProductVisit(user_id=current_user_id, product_id=product_id)
    db.session.add(visit)
    db.session.commit()
    return jsonify({'message': 'Visit recorded'}), 200


@recommendations.route('/user/recommendations')
@jwt_required()
def get_user_visits():
    if jwt_redis_blocklist.get(get_jwt()['jti']):
        return jsonify({'message': 'Token revoked'}), 401
        
    current_user_id = get_jwt_identity()
    
    # Get all visits for the current user, ordered by timestamp
    user_visits = UserProductVisit.query.filter_by(
        user_id=current_user_id
    ).order_by(UserProductVisit.visit_timestamp.desc()).all()
    
    visits_with_product_info = []
    for visit in user_visits:
        product_info = visit.product.to_dict()
        visit_info = visit.to_dict()
        visit_info['product'] = product_info
        visits_with_product_info.append(visit_info)

    return jsonify({
        'visits': visits_with_product_info
    }), 200