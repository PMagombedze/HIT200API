from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from models.db import db, User, Forum
import re
import pyotp
import os
from datetime import timedelta, datetime
from flask_mail import Mail, Message
import arrow

jwt = JWTManager()
mail = Mail()

auth = Blueprint('auth', __name__)

def checkEmail(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def checkPassword(password):
    return re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password)

#use pyotp for otp generation
totp = pyotp.TOTP(os.environ.get('OTP_SECRET'))
otp_ = totp.now()

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    password = data.get('password')
    email = data.get('email')

    if not password and not email:
        return jsonify({'message': 'Password and email are required'}), 400

    if not password:
        return jsonify({'message': 'Password is required'}), 400

    if not email:
        return jsonify({'message': 'Email is required'}), 400

    if not checkPassword(password):
            return jsonify({'message': 'Password not secure'}), 400
    
    if not checkEmail(email):
        return jsonify({'message': 'Invalid email format'}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({'message': 'Email already exists'}), 409

    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(minutes=15))
    return jsonify({'access_token': access_token, 'message': 'login succesful'}), 200


@auth.route('/verifyToken', methods=['POST'])
@jwt_required()
def verifyToken():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'message': 'Invalid token'}), 401
    user = User.query.filter_by(id=str(current_user)).first()
    expires_at = arrow.utcnow().shift(minutes=15, hours=2).isoformat()
    return jsonify({'message': 'Token is valid', 'user_id': current_user, 'expires_at': expires_at, 'email': user.email}), 200

@auth.route('/sendOtp', methods=['POST'])
@jwt_required()
def sendOtp():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'message': 'Invalid token'}), 401

    #send otp to user email
    user = User.query.get(current_user)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    msg = Message('Your OTP Code',
                  sender=os.environ.get('MAIL_USERNAME'),
                  recipients=[user.email])
    msg.body = f'Your OTP code is: {otp_}'

    try:
        mail.send(msg)
        return jsonify({'message': 'OTP sent successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to send OTP'}), 500

@auth.route('/verifyOtp', methods=['POST'])
@jwt_required()
def verifyOtp():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'message': 'Invalid token'}), 401
    data = request.get_json()
    otp = data.get('otp')
    if not otp:
        return jsonify({'message': 'OTP is required'}), 400
    if totp.verify(otp):
        return jsonify({'message': 'OTP verified successfully'}), 200
    else:
        return jsonify({'message': 'Invalid OTP'}), 401


