"""SQLALCHEMY DATABASE MODELS
"""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import uuid

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    """
    User Model
    """
    __tablename__ = 'users'
    id = db.Column(db.String(120), primary_key=True, default=str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, email, password, is_admin=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.is_admin = is_admin

    def __repr__(self):
        return '<User %r>' % self.email
    
    # bcrypt check password
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)


class Forum(db.Model):
    """
    Forum Model
    """
    __tablename__ = 'forums'
    id = db.Column(db.String(120), primary_key=True, default=str(uuid.uuid4()))
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now())
    user_id = db.Column(db.String(120), db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('forums', lazy=True))