from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from models.db import db, User, Forum
import re
import pyotp
import os
from datetime import timedelta, datetime
import arrow
import smtplib
from email.mime.text import MIMEText

jwt = JWTManager()

auth = Blueprint('auth', __name__)

def checkEmail(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def checkPassword(password):
    return re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password)

#use pyotp for otp generation
totp = pyotp.TOTP(os.environ.get('OTP_SECRET'))
otp_ = totp.at(datetime.now() + timedelta(minutes=15))

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
    userId = get_jwt_identity()
    user = User.query.filter_by(id=userId).first()
    if user:
        # Send the OTP to the user via email
        subject = "OTP Verification"
        sender = os.getenv('MAIL_USERNAME')
        recipients = [user.email]
        body = f"Hello,\n\n" \
                f"Your OTP for verification is: {otp_}\n\n" \
                f"Please enter this OTP to complete the verification process.\n\n" \
                f"Best regards,\n" \
                f"The Support Team"
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = 'PricePick Team'
        msg['To'] = ', '.join(recipients)

        try:
            # Set up the SMTP server
            with smtplib.SMTP(os.getenv('MAIL_SERVER'), os.getenv('MAIL_PORT')) as server:
                server.starttls()
                server.login(sender, os.getenv('MAIL_APP_PASSWORD'))
                server.sendmail(sender, recipients, msg.as_string())
            return {'message': 'OTP sent successfully'}, 200
        except Exception as e:
            return {"message": str(e)}, 500
    else:
        return {'message': 'User not found'}, 404

    try:
        mail.send(msg)
        return jsonify({'message': 'OTP sent successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to send OTP'}), 500

@auth.route('/verifyOtp', methods=['POST'])
@jwt_required()
def verifyOtp():
    data = request.get_json()
    otp = data.get('otp')
    if not otp:
        return jsonify({'message': 'OTP is required'}), 400
    if otp != otp_:
        return jsonify({'message': 'Invalid OTP'}), 401
    return jsonify({'message': 'OTP verified successfully'}), 200

@auth.route('/forgotPassword', methods=['POST'])
def forgotPassword():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'message': 'Email is required'}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    #send email with reset password link
    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(minutes=15))
    reset_link = f"http://localhost:5000/forgotpassword?token={access_token}"
    subject = "Password Reset Request"
    sender = os.getenv('MAIL_USERNAME')
    recipients = [user.email]
    body = f"Hello,\n\n" \
           f"To reset your password, please click the following link:\n" \
           f"{reset_link}\n\n" \
           f"If you did not request a password reset, please ignore this email.\n\n" \
           f"Best regards,\n" \
           f"The Support Team"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'PricePick Team'
    msg['To'] = ', '.join(recipients)

    try:
        # Set up the SMTP server
        with smtplib.SMTP(os.getenv('MAIL_SERVER'), os.getenv('MAIL_PORT')) as server:
            server.starttls()
            server.login(sender, os.getenv('MAIL_APP_PASSWORD'))
            server.sendmail(sender, recipients, msg.as_string())
        return jsonify({'message': 'Password reset email sent successfully'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500



