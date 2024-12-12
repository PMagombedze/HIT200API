from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt, JWTManager
from models.db import db, User, UserProfilePic
import re
import pyotp
import os
from datetime import timedelta, datetime
import arrow
import smtplib
from email.mime.text import MIMEText
from flask_bcrypt import generate_password_hash
import redis
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


jwt_redis_blocklist = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)


jwt = JWTManager()

auth = Blueprint('auth', __name__)

def checkEmail(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def checkPassword(password):
    return re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password)

# use pyotp for otp generation
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

@auth.route('/user/profile', methods=['POST'])
@jwt_required()
def userProfile():
    # check redis blocklist
    if jwt_redis_blocklist.get(get_jwt()['jti']):
        return jsonify({'message': 'Token revoked'}), 401
    user = User.query.filter_by(id=get_jwt_identity()).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    # upload profile pic
    if 'profile_pic' in request.files:
        file = request.files['profile_pic']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Check if user already has a profile pic
            existing_pic = UserProfilePic.query.filter_by(user_id=user.id).first()
            if existing_pic:
                return jsonify({'message': 'User already has a profile picture'}), 400
            file.save(os.path.join(os.getenv('UPLOAD_FOLDER'), filename))
            user_profile_pic = UserProfilePic(user_id=user.id, profile_pic=filename)
            db.session.add(user_profile_pic)
            db.session.commit()
            return jsonify({'message': 'Profile pic uploaded successfully'}), 200
        else:
            return jsonify({'message': 'Invalid file format'}), 400
    return jsonify({'message': 'Profile pic not found'}), 404

@auth.route('/user/profile', methods=['PUT'])
@jwt_required()
def updateProfile():
    # check redis blocklist
    if jwt_redis_blocklist.get(get_jwt()['jti']):
        return jsonify({'message': 'Token revoked'}), 401
    user = User.query.filter_by(id=get_jwt_identity()).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    # upload profile pic
    if 'profile_pic' in request.files:
        file = request.files['profile_pic']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(os.getenv('UPLOAD_FOLDER'), filename))
            # Check if user already has a profile pic
            existing_pic = UserProfilePic.query.filter_by(user_id=user.id).first()
            if existing_pic:
                existing_pic.profile_pic = filename
            else:
                user_profile_pic = UserProfilePic(user_id=user.id, profile_pic=filename)
                db.session.add(user_profile_pic)
            db.session.commit()
            return jsonify({'message': 'Profile pic updated successfully'}), 200
        else:
            return jsonify({'message': 'Invalid file format'}), 400
    return jsonify({'message': 'Profile pic not found'}), 404


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

    if user.is_admin:
        return jsonify({'message': 'Please use admin panel'}), 417

    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(minutes=15))
    return jsonify({'access_token': access_token, 'message': 'login successfull'}), 200


@auth.route('/verifyToken', methods=['POST'])
@jwt_required()
def verifyToken():
    jti = get_jwt()["jti"]
    if jwt_redis_blocklist.get(jti):
        return jsonify({'message': 'Token revoked'}), 401

    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({'message': 'Invalid token'}), 401
    user = User.query.filter_by(id=str(current_user)).first()
    expires_at = arrow.utcnow().shift(minutes=15, hours=2).isoformat()
    return jsonify({'message': 'Token is valid', 'user_id': current_user, 'expires_at': expires_at, 'email': user.email, 'is_admin': user.is_admin}), 200

@auth.route('/sendOtp', methods=['POST'])
@jwt_required()
def sendOtp():
    jti = get_jwt()["jti"]
    if jwt_redis_blocklist.get(jti):
        return jsonify({'message': 'Token revoked'}), 401

    userId = get_jwt_identity()
    user = User.query.filter_by(id=userId).first()
    if user:
        # Send the OTP to the user via email
        subject = "OTP Verification"
        sender = os.getenv('MAIL_USERNAME')
        recipients = [user.email]
        body = f"""
            <html>
                <body>
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #333;border: none; border-bottom:2px solid #000; padding-bottom: 4px;">OTP Verification</h2>
                        <p style="font-size: 10pt;">Hello,</p>
                        <p style="font-size: 10pt;">Your OTP for verification is:</p>
                        <div style="background-color: #f5f5f5; padding: 15px; margin: 20px 0; text-align: center; font-size: 24px; font-weight: bold;">
                            {otp_}
                        </div>
                        <p style="font-size: 10pt;">Please enter this OTP to complete the verification process.</p>
                        <p style="font-size: 10pt;">Best regards,<br>The Support Team</p>
                    </div>
                </body>
            </html>
            """
        msg = MIMEText(body, 'html')
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


@auth.route('/verifyOtp', methods=['POST'])
@jwt_required()
def verifyOtp():
    jti = get_jwt()["jti"]
    if jwt_redis_blocklist.get(jti):
        return jsonify({'message': 'Token revoked'}), 401

    userId = get_jwt_identity()
    data = request.get_json()
    otp = data.get('otp')
    if not otp:
        return jsonify({'message': 'OTP is required'}), 400
    if otp != otp_:
        return jsonify({'message': 'Invalid OTP'}), 401
    dash_access_token = create_access_token(identity=userId, expires_delta=timedelta(minutes=15))
    return jsonify({'message': 'OTP verified successfully', 'dash_token': dash_access_token}), 200

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
    body = f"""
        <html>
            <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #333;border: none; border-bottom:2px solid #000; padding-bottom: 4px;">Password Reset Request</h2>
                    <p style="font-size: 10pt;">Hello,</p>
                    <p style="font-size: 10pt;">To reset your password, please click the following link:</p>
                    <div style="background-color: #f5f5f5; padding: 15px; margin: 20px 0; text-align: center; font-size: 14px;">
                        <a href="{reset_link}" style="color: #1a73e8; text-decoration: none;">Reset Password</a>
                    </div>
                    <p style="font-size: 10pt;">If you did not request a password reset, please ignore this email.</p>
                    <p style="font-size: 10pt;">Best regards,<br>The Support Team</p>
                </div>
            </body>
        </html>
        """
    msg = MIMEText(body, 'html')
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

@auth.route('/resetPassword', methods=['POST'])
@jwt_required()
def resetPassword():
    # check if not in redis blocklist
    jti = get_jwt()["jti"]
    if jwt_redis_blocklist.get(jti):
        return jsonify({'message': 'Token revoked'}), 401

    data = request.get_json()
    password = data.get('password')
    if not password:
        return jsonify({'message': 'Password is required'}), 400
    if not checkPassword(password):
        return jsonify({'message': 'Password not secure'}), 400
    user =  User.query.filter_by(id=get_jwt_identity()).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    user.password = generate_password_hash(password)
    db.session.commit()
    return jsonify({'message': 'Password reset successfully'}), 200

# logout
@auth.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    jwt_redis_blocklist.set(jti, "revoked", ex=timedelta(days=30))
    return jsonify(msg="Access token revoked"), 200