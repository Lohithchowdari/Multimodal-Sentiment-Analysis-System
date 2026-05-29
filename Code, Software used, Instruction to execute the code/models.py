from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import pytz

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    
    # Relationships
    predictions = db.relationship('Prediction', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'

class Prediction(db.Model):
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    analysis_type = db.Column(db.String(50), nullable=False)  # text, image, audio
    input_data = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(50), nullable=False)  # positive, neutral, negative
    suggestion = db.Column(db.Text)
    email_sent = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    
    def __repr__(self):
        return f'<Prediction {self.id} - {self.sentiment}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'analysis_type': self.analysis_type,
            'input_data': self.input_data[:100] + '...' if len(self.input_data) > 100 else self.input_data,
            'sentiment': self.sentiment,
            'suggestion': self.suggestion,
            'email_sent': self.email_sent,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
