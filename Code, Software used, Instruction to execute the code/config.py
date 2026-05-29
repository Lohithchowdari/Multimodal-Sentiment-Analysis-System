import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///multimodal_sentiment.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Groq API
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
    
    # Admin
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'lohith'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or '8978188900'
    
    # App
    APP_NAME = os.environ.get('APP_NAME') or 'MindSync AI'
    
    # Upload folder
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size