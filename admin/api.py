from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, JWTManager
from models.db import db, User, Forum
import re
import pyotp
import os
from datetime import timedelta, datetime
import arrow
import smtplib
from email.mime.text import MIMEText

adminJwt = JWTManager()

admin = Blueprint('admin', __name__)

@admin.route('/users')
@jwt_required()
def userProfiles():
    user = User.query.filter_by(id=get_jwt_identity()).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    if not user.is_admin:
        return jsonify({'message': 'Fobbiden'}), 403
    users = User.query.all()
    return jsonify({'users': [user.to_dict() for user in users]}), 200

@admin.route('/users/<int:id>', methods=['DELETE'])
@jwt_required()
def deleteUser(id):
    user = User.query.filter_by(id=get_jwt_identity()).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    if not user.is_admin:
        return jsonify({'message': 'Fobbiden'}), 403
    user = User.query.filter_by(id=id).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200

@admin.route('/forums')
@jwt_required()
def forumProfiles():
    user = User.query.filter_by(id=get_jwt_identity()).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    if not user.is_admin:
        return jsonify({'message': 'Fobbiden'}), 403
    forums = Forum.query.all()
    return jsonify({'forums': [forum.to_dict() for forum in forums]}), 200

@admin.route('/forums/<int:id>', methods=['DELETE'])
@jwt_required()
def deleteForum(id):
    user = User.query.filter_by(id=get_jwt_identity()).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    if not user.is_admin:
        return jsonify({'message': 'Fobbiden'}), 403
    forum = Forum.query.filter_by(id=id).first()
    if not forum:
        return jsonify({'message': 'Forum not found'}), 404
    db.session.delete(forum)
    db.session.commit()
    return jsonify({'message': 'Forum deleted successfully'}), 200


