from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime

from db.mongo import get_db
from utils.security import hash_password, verify_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint for all user roles"""
    data = request.get_json()
    
    # Debug logging
    print(f"🔍 Login attempt - Received data: {data}")
    
    if not data or 'username' not in data or 'password' not in data:
        print("❌ Missing username or password in request")
        return jsonify({'error': 'Username and password required'}), 400
    
    username = data['username']
    password = data['password']
    
    print(f"🔍 Looking for user: {username}")
    
    db = get_db()
    user = db.users.find_one({'username': username})
    
    if not user:
        print(f"❌ User not found: {username}")
        print(f"💡 Hint: Have you run 'python seed_db.py' to create demo users?")
        return jsonify({'error': 'Invalid credentials'}), 401
    
    print(f"✅ User found: {username}")
    print(f"🔍 Verifying password...")
    
    if not verify_password(password, user['password']):
        print(f"❌ Password verification failed for user: {username}")
        return jsonify({'error': 'Invalid credentials'}), 401
    
    print(f"✅ Password verified successfully for user: {username}")
    
    # Check if user is enabled
    if not user.get('enabled', True):
        print(f"❌ User account is disabled: {username}")
        return jsonify({'error': 'Account is disabled. Please contact administrator.'}), 403
    
    print(f"✅ User account is enabled: {username}")
    
    # Create JWT token
    access_token = create_access_token(identity=str(user['_id']))
    
    # Get additional user info based on role
    user_info = {
        'id': str(user['_id']),
        'username': user['username'],
        'email': user.get('email', ''),
        'role': user['role'],
        'name': user.get('name', username)
    }
    
    # If student, get student_id
    if user['role'] == 'student':
        student = db.students.find_one({'user_id': str(user['_id'])})
        if student:
            user_info['student_id'] = student['student_id']
    
    return jsonify({
        'access_token': access_token,
        'user': user_info
    }), 200

@auth_bp.route('/register-student', methods=['POST'])
def register_student():
    """Register a new student (can be called by admin or self-registration)"""
    data = request.get_json()
    
    required_fields = ['username', 'password', 'email', 'name', 'student_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    db = get_db()
    
    # Check if username or email already exists
    if db.users.find_one({'username': data['username']}):
        return jsonify({'error': 'Username already exists'}), 409
    
    if db.users.find_one({'email': data['email']}):
        return jsonify({'error': 'Email already exists'}), 409
    
    if db.students.find_one({'student_id': data['student_id']}):
        return jsonify({'error': 'Student ID already exists'}), 409
    
    # Create user
    user_doc = {
        'username': data['username'],
        'password': hash_password(data['password']),
        'email': data['email'],
        'name': data['name'],
        'role': 'student',
        'created_at': datetime.utcnow()
    }
    
    user_result = db.users.insert_one(user_doc)
    user_id = str(user_result.inserted_id)
    
    # Create student profile
    student_doc = {
        'user_id': user_id,
        'student_id': data['student_id'],
        'name': data['name'],
        'email': data['email'],
        'department': data.get('department', ''),
        'year': data.get('year', ''),
        'face_registered': False,
        'created_at': datetime.utcnow()
    }
    
    db.students.insert_one(student_doc)
    
    return jsonify({
        'message': 'Student registered successfully',
        'student_id': data['student_id']
    }), 201

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    user_id = get_jwt_identity()
    db = get_db()
    
    user = db.users.find_one({'_id': ObjectId(user_id)})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user_info = {
        'id': str(user['_id']),
        'username': user['username'],
        'email': user.get('email', ''),
        'role': user['role'],
        'name': user.get('name', user['username'])
    }
    
    return jsonify(user_info), 200
