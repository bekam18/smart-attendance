import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # MongoDB
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'smart_attendance')
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_EXPIRY_HOURS', '168')))  # 7 days default
    
    # Recognition
    # Threshold set to 0.60 to accept faces with confidence 0.60+
    # This allows recognition of faces with confidence like 0.68, 0.82, etc.
    RECOGNITION_CONFIDENCE_THRESHOLD = 0.60
    MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'Classifier')
    
    # Upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    
    # CORS - Allow all localhost ports for development
    CORS_ORIGINS = ['http://localhost:5173', 'http://localhost:5174', 'http://localhost:3000', 
                    'http://127.0.0.1:5173', 'http://127.0.0.1:5174', 'http://127.0.0.1:3000']
    
    # Server
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', '5000'))

config = Config()
