from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure
from config import config
import sys

client = None
db = None

def init_db():
    """Initialize MongoDB connection"""
    global client, db
    
    try:
        client = MongoClient(config.MONGODB_URI, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        
        db = client[config.MONGODB_DB_NAME]
        
        # Create indexes
        create_indexes()
        
        print(f"✅ Connected to MongoDB: {config.MONGODB_DB_NAME}")
        return db
        
    except ConnectionFailure as e:
        print(f"❌ MongoDB connection failed: {e}")
        sys.exit(1)

def create_indexes():
    """Create database indexes for performance"""
    # Users collection
    db.users.create_index([('username', ASCENDING)], unique=True)
    db.users.create_index([('email', ASCENDING)], unique=True)
    db.users.create_index([('role', ASCENDING)])
    
    # Students collection
    db.students.create_index([('student_id', ASCENDING)], unique=True)
    db.students.create_index([('user_id', ASCENDING)])
    
    # Attendance collection
    db.attendance.create_index([('student_id', ASCENDING)])
    db.attendance.create_index([('session_id', ASCENDING)])
    db.attendance.create_index([('timestamp', ASCENDING)])
    db.attendance.create_index([('date', ASCENDING)])
    
    # Sessions collection
    db.sessions.create_index([('instructor_id', ASCENDING)])
    db.sessions.create_index([('start_time', ASCENDING)])
    db.sessions.create_index([('status', ASCENDING)])

def get_db():
    """Get database instance"""
    return db
