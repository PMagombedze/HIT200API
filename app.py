from flask import Flask, redirect, render_template
from models.db import db
from auth.api import auth, jwt
from admin.api import admin, adminJwt
from reviews.api import reviews
from recommendations.api import recommendations
from payments.api import payments
from notifications.api import notifications
from scraper.api import products
from flask_migrate import Migrate
from notifications.api import celery
from flask_cors import CORS


app = Flask(__name__)
app.config.from_object('config.Config')
migrate = Migrate(app, db)

# enable cors. don't allow api accesss from other domains
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

app.register_blueprint(auth, url_prefix='/api')
app.register_blueprint(admin, url_prefix='/api')
app.register_blueprint(reviews, url_prefix='/api')
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

@app.route('/u/profile')
def user_profile():
    return render_template('user/profile.html')

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

@app.route('/u/reviews')
def reviews_page():
    return render_template('user/reviews.html')

@app.route('/a/users')
def users():
    return render_template('admin/users.html')

@app.route('/a/notifications')
def support():
    return render_template('admin/notifications.html')

@app.route('/a/settings')
def settings():
    return render_template('admin/settings.html')

@app.route('/e/404')
def error_404():
    return render_template('error/404.html')

# 404 error
@app.errorhandler(404)
def page_not_found(e):
    return redirect('/e/404')

# 500 error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error/500.html'), 500

with app.app_context():
    db.init_app(app)
    db.create_all()
    adminJwt.init_app(app)
    jwt.init_app(app)
    celery.init_app(app)

if __name__ == '__main__':
    app.run(debug=True)
