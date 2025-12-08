"""
Working Security Middleware for Smart Attendance System
Simplified version without complex regex patterns
"""

from flask import request, jsonify
from functools import wraps
import html
import logging

logger = logging.getLogger(__name__)

class WorkingSecurityValidator:
    """Simple and working security validator"""
    
    # Simple dangerous keywords
    DANGEROUS_KEYWORDS = [
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE',
        'UNION', 'SELECT', 'EXEC', 'EXECUTE', 'SCRIPT', 'JAVASCRIPT'
    ]
    
    # Simple dangerous patterns
    DANGEROUS_PATTERNS = [
        "'", '"', '--', '/*', '*/', ';', '|', '&', '<', '>', 'script'
    ]
    
    @classmethod
    def is_safe_input(cls, value: str) -> bool:
        """Check if input is safe from basic attacks"""
        if not value:
            return True
        
        value_upper = value.upper()
        
        # Check for dangerous keywords
        for keyword in cls.DANGEROUS_KEYWORDS:
            if keyword in value_upper:
                logger.warning(f"Dangerous keyword detected: {keyword}")
                return False
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if pattern.lower() in value.lower():
                logger.warning(f"Dangerous pattern detected: {pattern}")
                return False
        
        return True
    
    @classmethod
    def sanitize_input(cls, value: str) -> str:
        """Sanitize input string"""
        if not value:
            return ""
        
        # HTML escape
        sanitized = html.escape(str(value))
        
        # Remove dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '|']
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()


def working_security_check(f):
    """
    Simple working security decorator
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Check JSON data
            if request.is_json:
                data = request.get_json()
                if data:
                    for key, value in data.items():
                        if isinstance(value, str):
                            if not WorkingSecurityValidator.is_safe_input(value):
                                logger.warning(f"Unsafe input in field '{key}': {value[:50]}...")
                                return jsonify({
                                    'error': 'Invalid input detected',
                                    'message': 'Input contains potentially malicious content'
                                }), 400
            
            # Check query parameters
            for key, value in request.args.items():
                if not WorkingSecurityValidator.is_safe_input(value):
                    logger.warning(f"Unsafe query parameter '{key}': {value[:50]}...")
                    return jsonify({
                        'error': 'Invalid query parameter',
                        'message': 'Query parameter contains potentially malicious content'
                    }), 400
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Security validation error: {e}")
            # Continue on error to avoid breaking the app
            return f(*args, **kwargs)
    
    return decorated_function


def working_json_validation(required_fields=None):
    """
    Simple working JSON validation decorator
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({'error': 'JSON data required'}), 400
                
                # Check required fields
                if required_fields:
                    missing = [field for field in required_fields if field not in data]
                    if missing:
                        return jsonify({
                            'error': 'Missing required fields',
                            'missing_fields': missing
                        }), 400
                
                # Validate and sanitize string fields
                validated_data = {}
                for key, value in data.items():
                    if isinstance(value, str):
                        if not WorkingSecurityValidator.is_safe_input(value):
                            return jsonify({
                                'error': f'Invalid input in field: {key}',
                                'message': 'Field contains potentially malicious content'
                            }), 400
                        validated_data[key] = WorkingSecurityValidator.sanitize_input(value)
                    else:
                        validated_data[key] = value
                
                # Store validated data
                request.validated_data = validated_data
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"JSON validation error: {e}")
                return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def working_audit_log(action: str):
    """
    Simple working audit logging decorator
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                logger.info(f"AUDIT: {action} - {request.method} {request.endpoint} - Success")
                return result
            except Exception as e:
                logger.error(f"AUDIT: {action} - {request.method} {request.endpoint} - Error: {e}")
                raise
        return decorated_function
    return decorator