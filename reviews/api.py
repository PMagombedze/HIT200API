from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity
from models.db import Reviews, db, User, Product
from auth.api import jwt_redis_blocklist

# user post a comment
reviews = Blueprint('reviews', __name__)

@reviews.route('/reviews/<string:id>', methods=['POST'])
@jwt_required()
def createreviews(id):
    if jwt_redis_blocklist.get(get_jwt()['jti']):
        return jsonify({'message': 'Token revoked'}), 401

    data = request.get_json()
    rating = data.get('rating')
    comment = data.get('comment')
    product_id = id

    # check if product exists
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    user_id = get_jwt_identity()
    if comment is None or comment == '':
        return jsonify({'message': 'Review is required'}), 400

    if type(rating) != int or rating < 1 or rating > 5:
        return jsonify({'message': 'Rating must be an integer between 1 and 5'}), 400

    reviews = Reviews(rating=rating, comment=comment, user_id=user_id, product_id=product_id)
    db.session.add(reviews)
    db.session.commit()
    return jsonify({'message': 'reviews created successfully'}), 201

@reviews.route('/reviews/<string:id>', methods=['GET'])
@jwt_required()
def getreviews(id):
    if jwt_redis_blocklist.get(get_jwt()['jti']):
        return jsonify({'message': 'Token revoked'}), 401
    
    product_id = id
    reviews = Reviews.query.filter_by(product_id=product_id).all()
    if not reviews:
        return jsonify({'message': 'No reviews for this product'}), 404
    reviews_list = []
    for review in reviews:
        user = User.query.get(review.user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        fname = user.first_name
        lname = user.last_name
        reviews_list.append({
            'id': review.id,
            'rating': review.rating,
            'comment': review.comment,
            'created_at': review.created_at,
            'product_id': review.product_id,
            'user': {
                'id': review.user.id,
                'client_name': f'{fname} {lname}',
            }
        })
    return jsonify(reviews_list), 200