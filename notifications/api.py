from email.mime.text import MIMEText
import os
import smtplib
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity
import requests
from auth.api import jwt_redis_blocklist
from models.db import User, db, Product
from celery import Celery
from celery.schedules import crontab

notifications = Blueprint('notifications', __name__)

celery = Celery('tasks', broker=os.environ.get('CELERY_BROKER_URL'))
celery.conf.broker_connection_retry_on_startup = True

CELERYBEAT_SCHEDULE = {
    'check-price-changes': {
        'task': 'notifications.tasks.check_price_changes',
        'schedule': crontab(minute='*/15')  # Runs every 15 minutes
    }
}


@celery.task
def check_price_changes():
    products = Product.query.all()
    for product in products:
        old_price = product.last_recorded_price
        current_price = product.price
        
        if old_price != current_price:
            notify_price_change.delay(product.id, old_price, current_price)
            product.last_recorded_price = current_price
            db.session.commit()

@celery.task
def notify_price_change(product_id, old_price, new_price):
    product = Product.query.get(product_id)
    users = User.query.all()
    if users.subscribed:
        notification = {
            'message': f'Price changed for {product.name} from ${old_price} to ${new_price}'
        }
        requests.post('http://localhost:5000/api/user/notifications', json=notification)


@notifications.route('/product/<int:product_id>/price', methods=['PUT'])
@jwt_required()
def update_product_price(product_id):
    if jwt_redis_blocklist.get(get_jwt()['jti']):
        return jsonify({'message': 'Token revoked'}), 401
        
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404
        
    new_price = request.json.get('price')
    if not new_price:
        return jsonify({'message': 'Price is required'}), 400
        
    product.price = new_price
    db.session.commit()
    
    # Trigger price check task
    check_price_changes.delay()
    
    return jsonify({'message': 'Price updated successfully'}), 200

@notifications.route('/user/notifications', methods=['POST'])
@jwt_required()
def create_notification():
    if jwt_redis_blocklist.get(get_jwt()['jti']):
        return jsonify({'message': 'Token revoked'}), 401
    data = request.get_json()
    message = data.get('message')

    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({'message': 'User not found'}), 404
    
    # send notification to user via email
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    subject = "Change in product price"
    sender = os.getenv('MAIL_USERNAME')
    recipients = [user.email]
    body = f"""
        <html>
            <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #333;border: none; border-bottom:2px solid #000; padding-bottom: 4px;">Change in product price</h2>
                    <p style="font-size: 10pt;">Hello,</p>
                    <div style="background-color: #f5f5f5; padding: 15px; margin: 20px 0; text-align: center; font-size: 14px;">
                        <a style="color: #000; text-decoration: none;">{message}</a>
                    </div>
                    <p style="font-size: 10pt;">Login to your account and secure this product whilst the deal lasts</p>
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
        return jsonify({'message': 'Notification sent successfully'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500
