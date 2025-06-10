from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Float, nullable=False)  # stored in cm
    weight = db.Column(db.Float, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    disease = db.Column(db.String(200))
    diet_preference = db.Column(db.String(50), nullable=False)
    budget = db.Column(db.String(50), nullable=False)
    goal = db.Column(db.String(50), nullable=False)
    cuisine = db.Column(db.String(50), nullable=False)

class DailyRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    day_number = db.Column(db.Integer, nullable=False)
    exercise = db.Column(db.Boolean, default=False)
    diet_followed = db.Column(db.Boolean, default=False)
    new_weight = db.Column(db.Float, nullable=False)

class DietPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    plan = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_bot = db.Column(db.Boolean, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
