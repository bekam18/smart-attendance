import bcrypt
from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from db.mysql import get_db

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def role_required(*allowed_roles):
    """
    Decorator to require specific roles.
    
    CRITICAL: Must be used AFTER @jwt_required() decorator:
    
    Correct order:
        @jwt_required()
        @role_required('instructor')
        def my_route():
            ...
    
    This ensures JWT is verified before we check roles.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # At this point, @jwt_required() has already verified the JWT
            # We can safely call get_jwt_identity() without RuntimeError
            user_id = get_jwt_identity()
            print(f"SECURITY DEBUG: Checking role for user {user_id}")
            
            db = get_db()
            result = db.execute_query("SELECT * FROM users WHERE id = %s", (user_id,))
            print(f"SECURITY DEBUG: Query result type: {type(result)}, length: {len(result) if result else 0}")
            user = result[0] if result else None
            print(f"SECURITY DEBUG: User extracted: {user is not None}")
            
            if not user:
                print(f"❌ User not found with ID: {user_id}")
                return jsonify({'error': 'User not found'}), 404
            
            # Check if user is enabled
            if not user.get('enabled', True):
                print(f"❌ User account is disabled: {user_id}")
                return jsonify({'error': 'Account is disabled. Please contact administrator.'}), 403
            
            print(f"✅ User role: {user['role']}, Required roles: {allowed_roles}")
            
            if user['role'] not in allowed_roles:
                print(f"❌ Insufficient permissions. User role: {user['role']}, Required: {allowed_roles}")
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator
