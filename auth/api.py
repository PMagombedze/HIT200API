from flask import Blueprint, make_response, request, jsonify, redirect, send_from_directory, url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt, JWTManager
from models.db import db, User, UserProfilePic, Product
from oauthlib.oauth2 import WebApplicationClient
import re
import pyotp
import os
from datetime import timedelta
import requests
import arrow
import smtplib
from email.mime.text import MIMEText
from flask_bcrypt import generate_password_hash
import redis
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from secrets import token_urlsafe
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

cookie_name = token_urlsafe(32)

load_dotenv()

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

totp = pyotp.TOTP(os.environ.get('OTP_SECRET'))
otp_ = totp.now()

@auth.route('/get-cookie')
def getCookie():
    return jsonify(cookie=cookie_name)

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    password = data.get('password')
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    city = data.get('city')

    if not password and not email:
        return jsonify({'message': 'Password and email are required'}), 400

    if not password:
        return jsonify({'message': 'Password is required'}), 400

    if not email:
        return jsonify({'message': 'Email is required'}), 400

    if not first_name:
        return jsonify({'message': 'First name is required'}), 400

    if not last_name:
        return jsonify({'message': 'Last name is required'}), 400

    if not city:
        return jsonify({'message': 'City is required'}), 400

    if not checkPassword(password):
        return jsonify({'message': 'Password not secure'}), 400

    if not checkEmail(email):
        return jsonify({'message': 'Invalid email format'}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({'message': 'Email already exists'}), 409

    user = User(email=email, password=password, first_name=first_name, last_name=last_name, city=city)
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
    if 'file' in request.files:
        file = request.files['file']
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

# display profile pic path
@auth.route('/user/profile', methods=['GET'])
@jwt_required()
def displayProfilePic():
    # check redis blocklist
    if jwt_redis_blocklist.get(get_jwt()['jti']):
        return jsonify({'message': 'Token revoked'}), 401
    user = User.query.filter_by(id=get_jwt_identity()).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    # get profile pic path
    profile_pic = UserProfilePic.query.filter_by(user_id=user.id).first()
    if not profile_pic:
        return jsonify({'img_url': '/api/uploads/user.svg', 'message': 'Profile pic not found', 'first_name': user.first_name, 'last_name': user.last_name, 'city': user.city, 'joined_at': user.joined_at, 'subscribed': user.subscribed, 'email': user.email}), 200
    return jsonify({'img_url': '/api/uploads/' + profile_pic.profile_pic, 'message': 'Profile pic found', 'first_name': user.first_name, 'last_name': user.last_name, 'city': user.city, 'joined_at': user.joined_at, 'subscribed': user.subscribed, 'email': user.email}), 200

@auth.route('/user/profile', methods=['DELETE'])
@jwt_required()
def deleteProfilePic():
    # check redis blocklist
    if jwt_redis_blocklist.get(get_jwt()['jti']):
        return jsonify({'message': 'Token revoked'}), 401
    user = User.query.filter_by(id=get_jwt_identity()).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    # get profile pic path
    profile_pic = UserProfilePic.query.filter_by(user_id=user.id).first()
    if not profile_pic:
        return jsonify({'message': 'Profile pic not found'}), 404
    # delete profile pic
    db.session.delete(profile_pic)
    db.session.commit()
    return jsonify({'message': 'Profile pic deleted successfully'}), 200

# get uploaded files
@auth.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.getenv('UPLOAD_FOLDER'), filename)

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
        return jsonify({'message': 'Invalid email or password'}), 400

    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(minutes=60))
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
    expires_at = arrow.utcnow().shift(minutes=60, hours=2).isoformat()
    return jsonify({'message': 'Token is valid', 'user_id': current_user, 'expires_at': expires_at, 'email': user.email, 'is_admin': user.is_admin, 'is_subscribed': user.subscribed}), 200

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
            return {"message": "Check your internet connection"}, 500
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
    dash_access_token = create_access_token(identity=userId, expires_delta=timedelta(minutes=60))
    return jsonify({'message': 'OTP verified successfully', 'dash_token': dash_access_token, 'cookie': cookie_name}), 200

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
    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(minutes=60))
    reset_link = f"http://localhost:5000/reset_password?token={access_token}"
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
        return jsonify({'message': "Check your internet connection"}), 500
    
# update profile
@auth.route('/updateProfile', methods=['PUT'])
@jwt_required()
def updateProfile():
    jti = get_jwt()["jti"]
    if jwt_redis_blocklist.get(jti):
        return jsonify({'message': 'Token revoked'}), 401
    userId = get_jwt_identity()
    if not userId:
        return jsonify({'message': 'User not found'}), 404
    user = User.query.filter_by(id=userId).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    email = data.get('email')
    password = data.get('password')

    if email:
        if not checkEmail(email):
            return jsonify({'message': 'Email not valid'}), 400
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != userId:
            return jsonify({'message': 'Email already exists'}), 400
        user.email = email
    if password:
        if not checkPassword(password):
            return jsonify({'message': 'Password not secure'}), 400
        user.password = generate_password_hash(password)
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'}), 200

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


GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

client = WebApplicationClient(GOOGLE_CLIENT_ID)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

# Configure Google OAuth
@auth.route('/google/login')
def google_login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri='https://localhost:5000/api/google/login/callback',
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)
   

@auth.route('/google/login/callback')
def google_callback():
    try:
        code = request.args.get("code")
        google_provider_cfg = get_google_provider_cfg()
        token_endpoint = google_provider_cfg["token_endpoint"]
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url='https://localhost:5000/api/google/login/callback',  # Match the exact redirect URI used in google_login
            code=code,
        )
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )
        client.parse_request_body_response(token_response.text)
        userinfo_response = requests.get(userinfo_endpoint, headers={"Authorization": f"Bearer {client.access_token}"})
        if userinfo_response.json().get("email_verified"):
            users_email = userinfo_response.json()["email"]
            picture = userinfo_response.json()["picture"]
            users_name = userinfo_response.json()["given_name"]
            users_last_name = userinfo_response.json()["family_name"]
            # Check if user already exists
            user = User.query.filter_by(email=users_email).first()
            if user:
                access_token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=60))
                response = make_response(redirect(url_for('user_dashboard')))
                response.set_cookie('dash_token', access_token)
                return response
            elif not user:
                # Create a new user in the database
                new_user = User(
                email=users_email,
                first_name=users_name,
                last_name=users_last_name,
                password=generate_password_hash('286755fad04869ca523320acce0dc6a4'),
                city='',
                )
                db.session.add(new_user)
                db.session.commit()
                # Add profile picture
                user_profile_pic = UserProfilePic(user_id=new_user.id, profile_pic=picture)
                db.session.add(user_profile_pic)
                db.session.commit()
            else:
                user_profile_pic = UserProfilePic.query.filter_by(user_id=user.id).first()
                if user_profile_pic:
                    user_profile_pic.profile_pic = picture
                else:
                    user_profile_pic = UserProfilePic(user_id=user.id, profile_pic=picture)
                    db.session.add(user_profile_pic)
                    db.session.commit()

            # create cookie called dash_token with access_token
            response = make_response(redirect(url_for('user_dashboard')))
            response.set_cookie('dash_token', create_access_token(identity=new_user.id, expires_delta=timedelta(minutes=60)))
            return response
        else:
            return redirect('/e/404'), 404
    except Exception:
        return redirect('/e/500'), 500

@auth.route('/api/verify-google-token', methods=['POST'])
def verify_google_token():
    try:
        # Get token from request
        request_data = request.get_json()
        token = request_data.get('token')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 400
        
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        # Get user info from the token
        users_email = idinfo['email']
        picture = idinfo.get('picture', '')
        users_name = idinfo.get('given_name', '')
        users_last_name = idinfo.get('family_name', '')
        
        # Check if email is verified
        if not idinfo.get('email_verified', False):
            return jsonify({'error': 'Email not verified'}), 400
            
        # Check if user already exists - similar to your callback logic
        user = User.query.filter_by(email=users_email).first()
        
        if user:
            # User exists, create access token
            access_token = create_access_token(
                identity=user.id, 
                expires_delta=timedelta(minutes=60)
            )
        else:
            # Create a new user in the database
            new_user = User(
                email=users_email,
                first_name=users_name,
                last_name=users_last_name,
                password=generate_password_hash('286755fad04869ca523320acce0dc6a4'),
                city='',
            )
            db.session.add(new_user)
            db.session.commit()
            
            # Add profile picture
            user_profile_pic = UserProfilePic(user_id=new_user.id, profile_pic=picture)
            db.session.add(user_profile_pic)
            db.session.commit()
            
            access_token = create_access_token(
                identity=new_user.id, 
                expires_delta=timedelta(minutes=60)
            )
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'user': {
                'email': users_email,
                'first_name': users_name,
                'last_name': users_last_name,
                'picture': picture,
                'id': user.id if user else new_user.id
            }
        }), 200
        
    except ValueError as e:
        # Invalid token
        return jsonify({'error': f'Invalid token: {str(e)}'}), 401
    except Exception as e:
        # Other errors
        return jsonify({'error': f'Authentication failed: {str(e)}'}), 500


@auth.route('/track_price', methods=['POST'])
@jwt_required()
def track_price():
    # check if not in redis blocklist
    jti = get_jwt()["jti"]
    if jwt_redis_blocklist.get(jti):
        return jsonify({'message': 'Token revoked'}), 401
    user = User.query.filter_by(id=get_jwt_identity()).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    if not user.subscribed:
        return jsonify(message='User is not subscribed')

    # get the product id from the request body
    data = request.get_json()
    product_name = data.get('product_name')
    if not product_name:
        return jsonify({'message': 'Product ID is required'}), 400
    
    subject = "Product Price Tracking"
    sender = os.getenv('MAIL_USERNAME')
    recipients = [user.email]
    body = f"""
        <html>
            <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #333;border: none; border-bottom:2px solid #000; padding-bottom: 4px;">Product Price Tracking</h2>
                    <p style="font-size: 10pt;">Hello,</p>
                    <p style="font-size: 10pt;">We are now tracking the price of the product <strong>{product_name}</strong>.</p>
                    <p style="font-size: 10pt;">You will be notified when there is a price change.</p>
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
        return jsonify({'message': 'Product is now being tracked. Check your email'}), 200
    except Exception as e:
        return jsonify({'message': "Check your internet connection"}), 500
