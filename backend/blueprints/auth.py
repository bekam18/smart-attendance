from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime

from db.mysql import get_db
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
    result = db.execute_query("SELECT * FROM users WHERE username = %s", (username,))
    user = result[0] if result else None
    
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
    access_token = create_access_token(identity=str(user['id']))
    
    # Get additional user info based on role
    user_info = {
        'id': str(user['id']),
        'username': user['username'],
        'email': user.get('email', ''),
        'role': user['role'],
        'name': user.get('name', username)
    }
    
    # If student, get student_id
    if user['role'] == 'student':
        student_result = db.execute_query("SELECT student_id FROM students WHERE user_id = %s", (user['id'],))
        if student_result:
            user_info['student_id'] = student_result[0]['student_id']
    
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
    existing_user = db.execute_query("SELECT id FROM users WHERE username = %s", (data['username'],))
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 409
    
    existing_email = db.execute_query("SELECT id FROM users WHERE email = %s", (data['email'],))
    if existing_email:
        return jsonify({'error': 'Email already exists'}), 409
    
    existing_student = db.execute_query("SELECT id FROM students WHERE student_id = %s", (data['student_id'],))
    if existing_student:
        return jsonify({'error': 'Student ID already exists'}), 409
    
    # Create user
    user_query = '''
        INSERT INTO users (username, password, email, name, role, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    '''
    user_id = db.execute_query(
        user_query,
        (data['username'], hash_password(data['password']), data['email'], 
         data['name'], 'student', datetime.utcnow()),
        fetch=False
    )
    
    # Create student profile
    student_query = '''
        INSERT INTO students (user_id, student_id, name, email, department, year, face_registered, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    '''
    db.execute_query(
        student_query,
        (user_id, data['student_id'], data['name'], data['email'],
         data.get('department', ''), data.get('year', ''), False, datetime.utcnow()),
        fetch=False
    )
    
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
    
    result = db.execute_query("SELECT * FROM users WHERE id = %s", (user_id,))
    user = result[0] if result else None
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user_info = {
        'id': str(user['id']),
        'username': user['username'],
        'email': user.get('email', ''),
        'role': user['role'],
        'name': user.get('name', user['username'])
    }
    
    return jsonify(user_info), 200


# Password Reset Endpoints
import secrets
from datetime import timedelta
from utils.email_service import email_service

# Store reset tokens in memory (in production, use Redis or database)
reset_tokens = {}

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset - sends email with reset token"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        db = get_db()
        
        # Find user by email
        result = db.execute_query("SELECT * FROM users WHERE email = %s", (email,))
        user = result[0] if result else None
        
        # Always return success to prevent email enumeration
        if not user:
            print(f"⚠️  Password reset requested for non-existent email: {email}")
            return jsonify({
                'message': 'If an account exists with this email, a password reset link has been sent.'
            }), 200
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        
        # Store token with expiration (1 hour)
        reset_tokens[reset_token] = {
            'user_id': user['id'],
            'email': email,
            'expires_at': datetime.now() + timedelta(hours=1)
        }
        
        # Send email
        email_sent = email_service.send_password_reset_email(
            to_email=email,
            reset_token=reset_token,
            user_name=user['name']
        )
        
        if email_sent:
            print(f"✅ Password reset email sent to: {email}")
        else:
            print(f"⚠️  Failed to send password reset email to: {email}")
            print(f"🔗 Reset token (for testing): {reset_token}")
        
        return jsonify({
            'message': 'If an account exists with this email, a password reset link has been sent.',
            'token': reset_token if not email_service.smtp_username else None  # Only for development
        }), 200
        
    except Exception as e:
        print(f"❌ Error in forgot_password: {e}")
        return jsonify({'error': 'Failed to process request'}), 500


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using token"""
    try:
        data = request.get_json()
        token = data.get('token', '').strip()
        new_password = data.get('password', '').strip()
        
        if not token or not new_password:
            return jsonify({'error': 'Token and new password are required'}), 400
        
        # Validate password strength
        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check if token exists and is valid
        if token not in reset_tokens:
            return jsonify({'error': 'Invalid or expired reset token'}), 400
        
        token_data = reset_tokens[token]
        
        # Check if token has expired
        if datetime.now() > token_data['expires_at']:
            del reset_tokens[token]
            return jsonify({'error': 'Reset token has expired'}), 400
        
        # Update password
        db = get_db()
        hashed_password = hash_password(new_password)
        
        db.execute_query(
            "UPDATE users SET password = %s WHERE id = %s",
            (hashed_password, token_data['user_id'])
        )
        
        # Delete used token
        del reset_tokens[token]
        
        print(f"✅ Password reset successful for user ID: {token_data['user_id']}")
        
        return jsonify({
            'message': 'Password has been reset successfully. You can now login with your new password.'
        }), 200
        
    except Exception as e:
        print(f"❌ Error in reset_password: {e}")
        return jsonify({'error': 'Failed to reset password'}), 500


@auth_bp.route('/verify-reset-token', methods=['POST'])
def verify_reset_token():
    """Verify if a reset token is valid"""
    try:
        data = request.get_json()
        token = data.get('token', '').strip()
        
        if not token:
            return jsonify({'valid': False, 'error': 'Token is required'}), 400
        
        if token not in reset_tokens:
            return jsonify({'valid': False, 'error': 'Invalid token'}), 400
        
        token_data = reset_tokens[token]
        
        if datetime.now() > token_data['expires_at']:
            del reset_tokens[token]
            return jsonify({'valid': False, 'error': 'Token has expired'}), 400
        
        return jsonify({
            'valid': True,
            'email': token_data['email']
        }), 200
        
    except Exception as e:
        print(f"❌ Error in verify_reset_token: {e}")
        return jsonify({'valid': False, 'error': 'Failed to verify token'}), 500
