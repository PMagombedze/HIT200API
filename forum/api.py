from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.db import Forum, User, db

# user post a comment
forum = Blueprint('forum', __name__)

@forum.route('/forum', methods=['POST'])
@jwt_required()
def createForum():
    data = request.get_json()
    rating = data.get('rating')
    comment = data.get('comment')
    user_id = get_jwt_identity()
    if not rating and not comment:
        return jsonify({'message': 'Title and description are required'}), 400
    
    if type(rating) != int or rating < 1 or rating > 5:
        return jsonify({'message': 'Rating must be an integer between 1 and 5'}), 400

    forum = Forum(rating=rating, comment=comment, user_id=user_id)
    db.session.add(forum)
    db.session.commit()
    return jsonify({'message': 'Forum created successfully'}), 201

@forum.route('/forum/<string:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def updateForum(id):
    if request.method == 'DELETE':
        user_id = get_jwt_identity()
        forum = Forum.query.filter_by(id=id).first()
        if not forum:
            return jsonify({'message': 'Forum not found'}), 404
        if forum.user_id != user_id:
            return jsonify({'message': 'Forbidden'}), 403
        db.session.delete(forum)
        db.session.commit()
        return jsonify({'message': 'Forum deleted successfully'}), 200

    if request.method == 'PUT':
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        user_id = get_jwt_identity()
        forum = Forum.query.filter_by(id=id).first()
        if not forum:
            return jsonify({'message': 'Forum not found'}), 404
        if forum.user_id != user_id:
            return jsonify({'message': 'Forbidden'}), 403
        if not title or not description:
            return jsonify({'message': 'Title and description are required'}), 400
        forum.title = title
        forum.description = description
        db.session.commit()
        return jsonify({'message': 'Forum updated successfully'}), 200