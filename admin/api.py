from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity, JWTManager, create_access_token
from models.db import db, User, Product, UserProfilePic, Notification
from datetime import timedelta
import json
import os
from auth.api import jwt_redis_blocklist

adminJwt = JWTManager()

admin = Blueprint('admin', __name__)

@admin.route('/admin/login', methods=['POST'])
def adminLogin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if not user.is_admin:
        return jsonify({'message': 'Email does not exist'}), 404

    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(minutes=60))
    return jsonify({'access_token': access_token, 'message': 'Login succesful'}), 200


@admin.route('/users')
@jwt_required()
def userProfiles():
    # check redis blocklist
    if jwt_redis_blocklist.get(get_jwt()['jti']):
        return jsonify({'message': 'Token revoked'}), 401

    user = User.query.filter_by(id=get_jwt_identity()).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    if not user.is_admin:
        return jsonify({'message': 'Forbidden'}), 403
    # Get users from database
    users = User.query.all()
    users_data = [user.to_dict() for user in users]
    # count number of users
    num_users = len(users_data)
    return jsonify({'users': users_data, 'num_users': num_users, 'message': 'Users retrieved'}), 200


@admin.route('/users/<string:id>', methods=['DELETE'])
@jwt_required()
def deleteUser(id):
    # check redis blocklist
    if jwt_redis_blocklist.get(get_jwt()['jti']):
        return jsonify({'message': 'Token revoked'}), 401
    user = User.query.filter_by(id=get_jwt_identity()).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    if not user.is_admin:
        return jsonify({'message': 'Fobbiden'}), 403
    user = User.query.filter_by(id=id).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Delete user profile picture if exists
    user_pic = UserProfilePic.query.filter_by(user_id=user.id).first()
    if user_pic:
        db.session.delete(user_pic)

    # Delete user notifications
    notifications = Notification.query.filter_by(user_id=user.id).all()
    for notification in notifications:
        db.session.delete(notification)

    # Delete user
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200

# notifications
@admin.route('/notifications', methods=['POST'])
@jwt_required()
def createNotification():
    # check redis blocklist
    if jwt_redis_blocklist.get(get_jwt()['jti']):
        return jsonify({'message': 'Token revoked'}), 401
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({'message': 'User not found'}), 404
    user = User.query.filter_by(id=user_id).first()
    if not user.is_admin:
        return jsonify({'message': 'Fobbiden'}), 403
    data = request.get_json()
    message = data.get('message')
    if not message:
        return jsonify({'message': 'Message is required'}), 400
    notification = Notification(message=message, user_id=user_id)
    db.session.add(notification)
    db.session.commit()
    return jsonify({'message': 'Notification created successfully'}), 201

@admin.route('/notifications', methods=['GET'])
@jwt_required()
def getNotifications():
    # check redis blocklist
    if jwt_redis_blocklist.get(get_jwt()['jti']):
        return jsonify({'message': 'Token revoked'}), 401
    user = User.query.filter_by(id=get_jwt_identity()).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    if not user.is_admin:
        return jsonify({'message': 'Fobbiden'}), 403
    notifications = Notification.query.all()
    notifications_data = []
    for notification in notifications:
        user = User.query.filter_by(id=notification.user_id).first()
        user_pic = UserProfilePic.query.filter_by(user_id=user.id).first()
        notifications_data.append({
            'notification': notification.to_dict(),
            'user': user.to_dict(),
            'profile_pic': user_pic.to_dict() if user_pic else {'profile_pic': 'user.svg'}
        })
    return jsonify({'notifications': notifications_data, 'message': 'Notifications retrieved successfully'}), 200
