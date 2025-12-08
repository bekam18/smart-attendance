"""
Simplified Security Middleware for Smart Attendance System
"""

from flask import request, jsonify, g
from functools import wraps
import re
import html
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class SimpleSecurityValidator:
    """Simple but effective security validator"""
    
    # SQL injection patterns
    SQL_PATTERNS = [
        r"'.*OR.*'.*'",  # ' OR '1'='1
        r"'.*OR.*\d.*=.*\d",  # ' OR 1=1
        r"--",  # SQL comments
        r"/\*.*\*/",  # Block comments
        r"UNION.*SELECT",  # UNION attacks
        r"DROP.*TABLE",  # DROP statements
        r"INSERT.*INTO",  # INSERT statements
        r"DELETE.*FROM",  # DELETE statements
        r"UPDATE.*SET",  # UPDATE statements
        r"EXEC\s*\(",  # EXEC function
        r"SLEEP\s*\(",  # SLEEP function
        r"BENCHMARK\s*\(",  # BENCHMARK function
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r"<script.*?>.*?</script>",
        r"javascript:",
        r"vbscript:",
        r"onload\s*=",
        r"onerror\s*=",
        r"onclick\s*=",
        r"<iframe.*?>",
        r"<object.*?>",
        r"<embed.*?>",
    ]
    
    @classmethod
    def is_safe_input(cls, value: str) -> bool:
        """Check if input is safe from SQL injection and XSS"""
        if not value:
            return True
        
        value_upper = value.upper()
        
        # Check SQL injection patterns
        for pattern in cls.SQL_PATTERNS:
            if re.search(pattern, value_upper, re.IGNORECASE):
                logger.warning(f"SQL injection pattern detected: {pattern}")
                return False
        
        # Check XSS patterns
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"XSS pattern detected: {pattern}")
                return False
        
        return True
    
    @classmethod
    def sanitize_input(cls, value: str) -> str:
        """Sanitize input string"""
        if not value:
            return ""
        
        # HTML escape
        sanitized = html.escape(str(value))
        
        # Remove null bytes and control characters
        sanitized = sanitized.replace('\x00', '')
        sanitized = re.sub(r'[\x01-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)
        
        return sanitized.strip()


def validate_request_security(f):
    """
    Simple decorator to validate request for security threats
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Check if request has JSON data
            if request.is_json:
                data = request.get_json()
                if data:
                    # Validate all string values in the JSON
                    for key, value in data.items():
                        if isinstance(value, str):
                            if not SimpleSecurityValidator.is_safe_input(value):
                                logger.warning(f"Unsafe input detected in field '{key}': {value[:50]}...")
                                return jsonify({
                                    'error': 'Invalid input detected',
                                    'message': 'Input contains potentially malicious content'
                                }), 400
            
            # Check query parameters
            for key, value in request.args.items():
                if not SimpleSecurityValidator.is_safe_input(value):
                    logger.warning(f"Unsafe query parameter '{key}': {value[:50]}...")
                    return jsonify({
                        'error': 'Invalid query parameter',
                        'message': 'Query parameter contains potentially malicious content'
                    }), 400
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Security validation error: {e}")
            # Don't fail on validation errors, just log and continue
            return f(*args, **kwargs)
    
    return decorated_function


def validate_json_fields(required_fields: List[str] = None, optional_fields: List[str] = None):
    """
    Decorator to validate JSON input fields
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
                
                # Validate and sanitize all fields
                validated_data = {}
                all_fields = (required_fields or []) + (optional_fields or [])
                
                for field in all_fields:
                    if field in data:
                        value = data[field]
                        if isinstance(value, str):
                            if not SimpleSecurityValidator.is_safe_input(value):
                                return jsonify({
                                    'error': f'Invalid input in field: {field}',
                                    'message': 'Field contains potentially malicious content'
                                }), 400
                            validated_data[field] = SimpleSecurityValidator.sanitize_input(value)
                        else:
                            validated_data[field] = value
                
                # Store validated data
                request.validated_data = validated_data
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"JSON validation error: {e}")
                # Don't fail on validation errors, just log and continue
                return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def audit_log_simple(action: str):
    """
    Simple audit logging decorator
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                
                # Log the action
                logger.info(f"AUDIT: {action} - {request.method} {request.endpoint} - Success")
                
                return result
                
            except Exception as e:
                logger.error(f"AUDIT: {action} - {request.method} {request.endpoint} - Error: {e}")
                raise
        
        return decorated_function
    return decorator


# Input format validators
def validate_username_format(username: str) -> bool:
    """Validate username format - allow alphanumeric, underscore, hyphen, dot"""
    if not username or len(username) < 1 or len(username) > 50:
        return False
    return re.match(r'^[a-zA-Z0-9._-]+$', username) is not None


def validate_email_format(email: str) -> bool:
    """Validate email format"""
    if not email or len(email) > 254:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_student_id_format(student_id: str) -> bool:
    """Validate student ID format"""
    if not student_id:
        return False
    pattern = r'^[A-Z]{3}[0-9]{3}$'  # STU001 format
    return re.match(pattern, student_id) is not None