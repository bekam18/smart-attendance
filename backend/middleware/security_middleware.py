"""
Security Middleware for Smart Attendance System
Provides automatic request validation and security checks
"""

from flask import request, jsonify, g
from functools import wraps
from typing import Dict, Any, List, Optional
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta

from utils.sql_security import SQLSecurityValidator, log_security_event

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """
    Security middleware for request validation and rate limiting
    """
    
    def __init__(self):
        self.validator = SQLSecurityValidator()
        self.rate_limit_storage = defaultdict(list)
        self.blocked_ips = set()
        self.suspicious_patterns = defaultdict(int)
    
    def validate_request(self, f):
        """
        Decorator to validate incoming requests for security threats
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Get client IP
                client_ip = self._get_client_ip()
                
                # Check if IP is blocked
                if client_ip in self.blocked_ips:
                    log_security_event("BLOCKED_IP_ACCESS", {"ip": client_ip})
                    return jsonify({'error': 'Access denied'}), 403
                
                # Rate limiting
                if not self._check_rate_limit(client_ip):
                    log_security_event("RATE_LIMIT_EXCEEDED", {"ip": client_ip})
                    return jsonify({'error': 'Rate limit exceeded'}), 429
                
                # Validate request headers
                if not self._validate_headers():
                    log_security_event("INVALID_HEADERS", {"ip": client_ip})
                    return jsonify({'error': 'Invalid request headers'}), 400
                
                # Validate request data if present
                if request.is_json and request.get_json():
                    data = request.get_json()
                    validation_errors = self._validate_request_data(data)
                    
                    if validation_errors:
                        self._track_suspicious_activity(client_ip, "INVALID_INPUT")
                        log_security_event("INVALID_INPUT", {
                            "ip": client_ip,
                            "errors": validation_errors
                        })
                        return jsonify({
                            'error': 'Invalid input detected',
                            'details': 'Request contains potentially malicious content'
                        }), 400
                
                # Store client info in request context
                g.client_ip = client_ip
                g.request_validated = True
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Security middleware error: {e}")
                return jsonify({'error': 'Security validation failed'}), 500
        
        return decorated_function
    
    def _get_client_ip(self) -> str:
        """Get client IP address from request"""
        # Check for forwarded headers first
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr or 'unknown'
    
    def _check_rate_limit(self, client_ip: str, max_requests: int = 100, 
                         window_minutes: int = 15) -> bool:
        """
        Check if client has exceeded rate limit
        
        Args:
            client_ip: Client IP address
            max_requests: Maximum requests allowed
            window_minutes: Time window in minutes
            
        Returns:
            bool: True if within rate limit
        """
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        
        # Clean old entries
        self.rate_limit_storage[client_ip] = [
            timestamp for timestamp in self.rate_limit_storage[client_ip]
            if timestamp > window_start
        ]
        
        # Check current count
        current_count = len(self.rate_limit_storage[client_ip])
        
        if current_count >= max_requests:
            # Block IP if consistently exceeding limits
            if current_count > max_requests * 2:
                self.blocked_ips.add(client_ip)
                logger.warning(f"IP blocked for excessive requests: {client_ip}")
            return False
        
        # Add current request
        self.rate_limit_storage[client_ip].append(now)
        return True
    
    def _validate_headers(self) -> bool:
        """Validate request headers for security"""
        # Check for required headers in API requests
        if request.path.startswith('/api/'):
            # Validate Content-Type for POST/PUT requests
            if request.method in ['POST', PUT'] and not request.is_json:
                if 'multipart/form-data' not in request.content_type:
                    return False
        
        # Check for suspicious headers
        suspicious_headers = [
            'X-Forwarded-Host',
            'X-Originating-IP',
            'X-Remote-IP',
            'X-Remote-Addr'
        ]
        
        for header in suspicious_headers:
            if header in request.headers:
                value = request.headers.get(header)
                if not self.validator.validate_input(value, header):
                    return False
        
        return True
    
    def _validate_request_data(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate request JSON data"""
        return self.validator.validate_json_data(data)
    
    def _track_suspicious_activity(self, client_ip: str, activity_type: str):
        """Track suspicious activity patterns"""
        key = f"{client_ip}:{activity_type}"
        self.suspicious_patterns[key] += 1
        
        # Block IP if too many suspicious activities
        if self.suspicious_patterns[key] > 10:
            self.blocked_ips.add(client_ip)
            logger.warning(f"IP blocked for suspicious activity: {client_ip}")


# Global middleware instance
security_middleware = SecurityMiddleware()


def require_security_validation(f):
    """
    Decorator to require security validation for endpoints
    """
    return security_middleware.validate_request(f)


def validate_json_input(required_fields: Optional[List[str]] = None,
                       optional_fields: Optional[List[str]] = None,
                       custom_validators: Optional[Dict[str, callable]] = None):
    """
    Advanced decorator for JSON input validation
    
    Args:
        required_fields: List of required field names
        optional_fields: List of optional field names
        custom_validators: Dictionary of field-specific validators
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Get and validate JSON data
                data = request.get_json()
                
                if not data:
                    return jsonify({'error': 'JSON data required'}), 400
                
                # Check required fields
                if required_fields:
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        return jsonify({
                            'error': 'Missing required fields',
                            'missing_fields': missing_fields
                        }), 400
                
                # Validate field formats
                validation_errors = {}
                
                # General security validation
                security_errors = SQLSecurityValidator.validate_json_data(data)
                validation_errors.update(security_errors)
                
                # Custom field validation
                if custom_validators:
                    for field, validator in custom_validators.items():
                        if field in data:
                            try:
                                if not validator(data[field]):
                                    validation_errors[field] = [f'Invalid {field} format']
                            except Exception as e:
                                validation_errors[field] = [f'Validation error: {str(e)}']
                
                if validation_errors:
                    return jsonify({
                        'error': 'Validation failed',
                        'validation_errors': validation_errors
                    }), 400
                
                # Sanitize input
                sanitized_data = {}
                all_fields = (required_fields or []) + (optional_fields or [])
                
                for field in all_fields:
                    if field in data:
                        sanitized_data[field] = SQLSecurityValidator.sanitize_input(data[field])
                
                # Store sanitized data in request context
                request.validated_data = sanitized_data
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Input validation error: {e}")
                return jsonify({'error': 'Input validation failed'}), 500
        
        return decorated_function
    return decorator


def audit_log(action: str, resource: str = None):
    """
    Decorator to log API actions for audit purposes
    
    Args:
        action: Action being performed
        resource: Resource being accessed
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            try:
                # Execute the function
                result = f(*args, **kwargs)
                
                # Log successful action
                duration = time.time() - start_time
                
                log_data = {
                    'action': action,
                    'resource': resource,
                    'method': request.method,
                    'endpoint': request.endpoint,
                    'duration_ms': round(duration * 1000, 2),
                    'status': 'success'
                }
                
                if hasattr(g, 'client_ip'):
                    log_data['client_ip'] = g.client_ip
                
                logger.info(f"AUDIT: {log_data}")
                
                return result
                
            except Exception as e:
                # Log failed action
                duration = time.time() - start_time
                
                log_data = {
                    'action': action,
                    'resource': resource,
                    'method': request.method,
                    'endpoint': request.endpoint,
                    'duration_ms': round(duration * 1000, 2),
                    'status': 'error',
                    'error': str(e)
                }
                
                if hasattr(g, 'client_ip'):
                    log_data['client_ip'] = g.client_ip
                
                logger.error(f"AUDIT: {log_data}")
                
                raise
        
        return decorated_function
    return decorator


# Security headers middleware
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response


# Input sanitization utilities
class InputSanitizer:
    """Utility class for input sanitization"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            value = str(value)
        
        # Remove null bytes and control characters
        sanitized = value.replace('\x00', '').strip()
        
        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return SQLSecurityValidator.sanitize_input(sanitized)
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """Sanitize email input"""
        from utils.sql_security import validate_email
        
        sanitized = InputSanitizer.sanitize_string(email, 254)
        
        if not validate_email(sanitized):
            raise ValueError("Invalid email format")
        
        return sanitized.lower()
    
    @staticmethod
    def sanitize_username(username: str) -> str:
        """Sanitize username input"""
        from utils.sql_security import validate_username
        
        sanitized = InputSanitizer.sanitize_string(username, 50)
        
        if not validate_username(sanitized):
            raise ValueError("Invalid username format")
        
        return sanitized
    
    @staticmethod
    def sanitize_student_id(student_id: str) -> str:
        """Sanitize student ID input"""
        from utils.sql_security import validate_student_id
        
        sanitized = InputSanitizer.sanitize_string(student_id, 10).upper()
        
        if not validate_student_id(sanitized):
            raise ValueError("Invalid student ID format")
        
        return sanitized