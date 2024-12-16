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

app.register_blueprint(auth, url_prefix='/api')
app.register_blueprint(admin, url_prefix='/api')
app.register_blueprint(forum, url_prefix='/api')
app.register_blueprint(recommendations, url_prefix='/api')
app.register_blueprint(payments, url_prefix='/api')
app.register_blueprint(notifications, url_prefix='/api')
app.register_blueprint(products, url_prefix='/api')


# routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reset/success')
def reset_success():
    return render_template('user/reset_success.html')


@app.route('/a/dashboard')
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route('/u/dashboard')
def user_dashboard():
    return render_template('user/dashboard.html')

@app.route('/admin/login')
def admin_login():
    return render_template('admin/login.html')

@app.route('/login')
def user_login():
    return render_template('user/login.html')

@app.route('/register')
def user_register():
    return render_template('user/signup.html')

@app.route('/otp')
def otp():
    return render_template('user/otp.html')

@app.route('/admin/otp')
def adminOtp():
    return render_template('admin/otp.html')

@app.route('/forgot_password')
def forgot_password():
    return render_template('user/forgotpass.html')

@app.route('/reset_password')
def reset_password():
    return render_template('user/resetpass.html')


with app.app_context():
    db.init_app(app)
    db.create_all()
    adminJwt.init_app(app)
    jwt.init_app(app)
    celery.init_app(app)

if __name__ == '__main__':
    app.run(debug=True)