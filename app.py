from flask import Flask, render_template
from models.db import db
from auth.api import auth, jwt
from admin.api import admin, adminJwt
from forum.api import forum
from recommendations.api import recommendations
from payments.api import payments
from notifications.api import notifications
from scraper.api import products
from flask_migrate import Migrate
from notifications.api import celery


app = Flask(__name__)
app.config.from_object('config.Config')
migrate = Migrate(app, db)

@app.route('/')
def index():
    return render_template('index.html')

app.register_blueprint(auth, url_prefix='/api')
app.register_blueprint(admin, url_prefix='/api')
app.register_blueprint(forum, url_prefix='/api')
app.register_blueprint(recommendations, url_prefix='/api')
app.register_blueprint(payments, url_prefix='/api')
app.register_blueprint(notifications, url_prefix='/api')
app.register_blueprint(products, url_prefix='/api')


with app.app_context():
    db.init_app(app)
    db.create_all()
    adminJwt.init_app(app)
    jwt.init_app(app)
    celery.init_app(app)

if __name__ == '__main__':
    app.run()