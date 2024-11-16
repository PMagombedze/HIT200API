from flask import Flask
from models.db import db
from auth.api import auth, jwt
from admin.api import admin, adminJwt
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object('config.Config')
migrate = Migrate(app, db)

app.register_blueprint(auth, url_prefix='/api')
app.register_blueprint(admin, url_prefix='/api')


with app.app_context():
    db.init_app(app)
    db.create_all()
    adminJwt.init_app(app)
    jwt.init_app(app)

if __name__ == '__main__':
    app.run()