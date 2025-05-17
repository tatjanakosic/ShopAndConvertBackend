from app import db
from datetime import datetime
from enum import Enum

class PurchaseStatus(Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    surname = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(120), nullable=False)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), nullable=False)
    expiry = db.Column(db.String(10), nullable=False)
    cvv = db.Column(db.String(4), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String(10), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default=PurchaseStatus.PENDING.value)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
