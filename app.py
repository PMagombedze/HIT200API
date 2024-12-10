from flask import Flask
import requests
from models.db import Product, db, User
from auth.api import auth, jwt
from admin.api import admin, adminJwt
from forum.api import forum
from recommendations.api import recommendations
from payments.api import payments
from notifications.api import notifications
from flask_migrate import Migrate
from celery import Celery
from celery.schedules import crontab


app = Flask(__name__)
app.config.from_object('config.Config')
migrate = Migrate(app, db)

celery = Celery('tasks', broker=app.config['CELERY_BROKER_URL'])

app.register_blueprint(auth, url_prefix='/api')
app.register_blueprint(admin, url_prefix='/api')
app.register_blueprint(forum, url_prefix='/api')
app.register_blueprint(recommendations, url_prefix='/api')
app.register_blueprint(payments, url_prefix='/api')
app.register_blueprint(notifications, url_prefix='/api')

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


with app.app_context():
    db.init_app(app)
    db.create_all()
    adminJwt.init_app(app)
    jwt.init_app(app)

if __name__ == '__main__':
    app.run()