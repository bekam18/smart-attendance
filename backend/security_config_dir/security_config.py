"""
Security Configuration for Smart Attendance System
Centralized security settings and policies
"""

import os
from datetime import timedelta

class SecurityConfig:
    """Security configuration settings"""
    
    # SQL Injection Protection
    SQL_INJECTION_PROTECTION_ENABLED = True
    VALIDATE_ALL_INPUTS = True
    LOG_SECURITY_EVENTS = True
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_REQUESTS_PER_MINUTE = 60
    RATE_LIMIT_REQUESTS_PER_HOUR = 1000
    RATE_LIMIT_BURST_THRESHOLD = 10
    
    # IP Blocking
    AUTO_BLOCK_SUSPICIOUS_IPS = True
    SUSPICIOUS_ACTIVITY_THRESHOLD = 10
    BLOCK_DURATION_HOURS = 24
    
    # Input Validation
    MAX_STRING_LENGTH = 1000
    MAX_EMAIL_LENGTH = 254
    MAX_USERNAME_LENGTH = 50
    MAX_PASSWORD_LENGTH = 128
    MIN_PASSWORD_LENGTH = 6
    
    # File Upload Security
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_FILE_SIZE_MB = 10
    SCAN_UPLOADED_FILES = True
    
    # Session Security
    SESSION_TIMEOUT_MINUTES = 30
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    REQUIRE_HTTPS_IN_PRODUCTION = True
    
    # Password Security
    PASSWORD_HASH_ROUNDS = 12
    REQUIRE_STRONG_PASSWORDS = True
    PASSWORD_MIN_COMPLEXITY_SCORE = 3
    PREVENT_PASSWORD_REUSE = True
    PASSWORD_HISTORY_COUNT = 5
    
    # Audit Logging
    AUDIT_LOG_ENABLED = True
    AUDIT_LOG_FILE = 'logs/audit.log'
    SECURITY_LOG_FILE = 'logs/security.log'
    LOG_RETENTION_DAYS = 90
    
    # Database Security
    USE_PREPARED_STATEMENTS = True
    VALIDATE_SQL_QUERIES = True
    LOG_DATABASE_QUERIES = False  # Set to True for debugging
    DATABASE_CONNECTION_TIMEOUT = 30
    
    # API Security
    REQUIRE_API_KEY_FOR_EXTERNAL = False
    API_KEY_HEADER = 'X-API-Key'
    CORS_STRICT_MODE = True
    VALIDATE_CONTENT_TYPE = True
    
    # Encryption
    ENCRYPT_SENSITIVE_DATA = True
    ENCRYPTION_ALGORITHM = 'AES-256-GCM'
    KEY_ROTATION_DAYS = 90
    
    # Security Headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'camera=(), microphone=(), geolocation=()'
    }
    
    # Monitoring and Alerting
    MONITOR_FAILED_LOGINS = True
    FAILED_LOGIN_THRESHOLD = 5
    FAILED_LOGIN_WINDOW_MINUTES = 15
    ALERT_ON_SECURITY_EVENTS = True
    
    # Face Recognition Security
    FACE_RECOGNITION_CONFIDENCE_THRESHOLD = 0.6
    MAX_FACE_REGISTRATION_ATTEMPTS = 3
    REQUIRE_LIVE_DETECTION = True
    PREVENT_PHOTO_SPOOFING = True
    
    # Data Privacy
    ANONYMIZE_LOGS = True
    GDPR_COMPLIANCE_MODE = True
    DATA_RETENTION_POLICY_DAYS = 365
    ALLOW_DATA_EXPORT = True
    REQUIRE_CONSENT_FOR_BIOMETRIC_DATA = True


class SecurityPolicies:
    """Security policies and rules"""
    
    # Password Policy
    PASSWORD_POLICY = {
        'min_length': SecurityConfig.MIN_PASSWORD_LENGTH,
        'max_length': SecurityConfig.MAX_PASSWORD_LENGTH,
        'require_uppercase': True,
        'require_lowercase': True,
        'require_numbers': True,
        'require_special_chars': False,
        'forbidden_patterns': [
            'password', '123456', 'qwerty', 'admin', 'user',
            'attendance', 'smart', 'system'
        ]
    }
    
    # Account Lockout Policy
    ACCOUNT_LOCKOUT_POLICY = {
        'max_failed_attempts': 5,
        'lockout_duration_minutes': 30,
        'reset_failed_attempts_after_minutes': 60,
        'notify_admin_on_lockout': True
    }
    
    # Data Access Policy
    DATA_ACCESS_POLICY = {
        'admin': ['all'],
        'instructor': ['own_courses', 'own_students', 'own_sessions'],
        'student': ['own_data', 'own_attendance']
    }
    
    # Audit Policy
    AUDIT_POLICY = {
        'log_all_api_calls': True,
        'log_database_changes': True,
        'log_authentication_events': True,
        'log_authorization_failures': True,
        'log_data_access': True,
        'log_configuration_changes': True
    }


class SecurityValidators:
    """Security validation rules"""
    
    @staticmethod
    def validate_password_strength(password: str) -> dict:
        """
        Validate password strength according to policy
        
        Args:
            password: Password to validate
            
        Returns:
            dict: Validation result with score and feedback
        """
        policy = SecurityPolicies.PASSWORD_POLICY
        score = 0
        feedback = []
        
        # Length check
        if len(password) < policy['min_length']:
            feedback.append(f"Password must be at least {policy['min_length']} characters")
        elif len(password) >= policy['min_length']:
            score += 1
        
        if len(password) > policy['max_length']:
            feedback.append(f"Password must not exceed {policy['max_length']} characters")
        
        # Character requirements
        if policy['require_uppercase'] and not any(c.isupper() for c in password):
            feedback.append("Password must contain at least one uppercase letter")
        elif policy['require_uppercase']:
            score += 1
        
        if policy['require_lowercase'] and not any(c.islower() for c in password):
            feedback.append("Password must contain at least one lowercase letter")
        elif policy['require_lowercase']:
            score += 1
        
        if policy['require_numbers'] and not any(c.isdigit() for c in password):
            feedback.append("Password must contain at least one number")
        elif policy['require_numbers']:
            score += 1
        
        if policy['require_special_chars'] and not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            feedback.append("Password must contain at least one special character")
        elif policy['require_special_chars']:
            score += 1
        
        # Forbidden patterns
        password_lower = password.lower()
        for pattern in policy['forbidden_patterns']:
            if pattern in password_lower:
                feedback.append(f"Password cannot contain '{pattern}'")
                score = max(0, score - 1)
        
        return {
            'score': score,
            'max_score': 4,
            'is_strong': score >= SecurityConfig.PASSWORD_MIN_COMPLEXITY_SCORE,
            'feedback': feedback
        }
    
    @staticmethod
    def validate_file_upload(filename: str, file_size: int) -> dict:
        """
        Validate file upload according to security policy
        
        Args:
            filename: Name of uploaded file
            file_size: Size of uploaded file in bytes
            
        Returns:
            dict: Validation result
        """
        errors = []
        
        # Check file extension
        if '.' not in filename:
            errors.append("File must have an extension")
        else:
            extension = filename.rsplit('.', 1)[1].lower()
            if extension not in SecurityConfig.ALLOWED_IMAGE_EXTENSIONS:
                errors.append(f"File type not allowed. Allowed types: {', '.join(SecurityConfig.ALLOWED_IMAGE_EXTENSIONS)}")
        
        # Check file size
        max_size_bytes = SecurityConfig.MAX_FILE_SIZE_MB * 1024 * 1024
        if file_size > max_size_bytes:
            errors.append(f"File size exceeds maximum allowed size of {SecurityConfig.MAX_FILE_SIZE_MB}MB")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }


# Environment-specific security settings
def get_security_config():
    """Get security configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        # Production security settings
        SecurityConfig.RATE_LIMIT_REQUESTS_PER_MINUTE = 30
        SecurityConfig.REQUIRE_HTTPS_IN_PRODUCTION = True
        SecurityConfig.LOG_DATABASE_QUERIES = False
        SecurityConfig.CORS_STRICT_MODE = True
    elif env == 'testing':
        # Testing security settings
        SecurityConfig.RATE_LIMIT_ENABLED = False
        SecurityConfig.AUTO_BLOCK_SUSPICIOUS_IPS = False
        SecurityConfig.LOG_SECURITY_EVENTS = False
    
    return SecurityConfig


# Security event types for logging
class SecurityEventTypes:
    """Security event type constants"""
    
    # Authentication events
    LOGIN_SUCCESS = 'LOGIN_SUCCESS'
    LOGIN_FAILURE = 'LOGIN_FAILURE'
    LOGOUT = 'LOGOUT'
    PASSWORD_RESET_REQUEST = 'PASSWORD_RESET_REQUEST'
    PASSWORD_RESET_SUCCESS = 'PASSWORD_RESET_SUCCESS'
    ACCOUNT_LOCKED = 'ACCOUNT_LOCKED'
    
    # Authorization events
    ACCESS_DENIED = 'ACCESS_DENIED'
    PRIVILEGE_ESCALATION_ATTEMPT = 'PRIVILEGE_ESCALATION_ATTEMPT'
    UNAUTHORIZED_DATA_ACCESS = 'UNAUTHORIZED_DATA_ACCESS'
    
    # Input validation events
    SQL_INJECTION_ATTEMPT = 'SQL_INJECTION_ATTEMPT'
    XSS_ATTEMPT = 'XSS_ATTEMPT'
    INVALID_INPUT = 'INVALID_INPUT'
    FILE_UPLOAD_VIOLATION = 'FILE_UPLOAD_VIOLATION'
    
    # Rate limiting events
    RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED'
    IP_BLOCKED = 'IP_BLOCKED'
    SUSPICIOUS_ACTIVITY = 'SUSPICIOUS_ACTIVITY'
    
    # Data events
    DATA_EXPORT = 'DATA_EXPORT'
    DATA_MODIFICATION = 'DATA_MODIFICATION'
    SENSITIVE_DATA_ACCESS = 'SENSITIVE_DATA_ACCESS'
    
    # System events
    CONFIGURATION_CHANGE = 'CONFIGURATION_CHANGE'
    SECURITY_POLICY_VIOLATION = 'SECURITY_POLICY_VIOLATION'
    SYSTEM_ERROR = 'SYSTEM_ERROR'