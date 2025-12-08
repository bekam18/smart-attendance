"""
SQL Security Utilities for Smart Attendance System
Provides additional layers of protection against SQL injection attacks
"""

import re
import html
from typing import Any, Dict, List, Optional, Union
from functools import wraps
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)

class SQLSecurityValidator:
    """
    SQL Security Validator class to prevent SQL injection attacks
    """
    
    # Dangerous SQL keywords that should be blocked in user input
    DANGEROUS_KEYWORDS = [
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE',
        'EXEC', 'EXECUTE', 'UNION', 'SELECT', 'SCRIPT', 'JAVASCRIPT',
        'VBSCRIPT', 'ONLOAD', 'ONERROR', 'ONCLICK', 'SCRIPT', 'IFRAME',
        'OBJECT', 'EMBED', 'FORM', 'INPUT', 'TEXTAREA', 'BUTTON'
    ]
    
    # SQL injection patterns to detect
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE|UNION)\b)",
        r"(--|#|/\*|\*/)",  # SQL comments
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",  # OR 1=1, AND 1=1
        r"(\b(OR|AND)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",  # OR 'a'='a'
        r"(;|\|\||&&)",  # Command separators
        r"(\bUNION\s+SELECT\b)",  # UNION SELECT
        r"(\bINTO\s+OUTFILE\b)",  # INTO OUTFILE
        r"(\bLOAD_FILE\b)",  # LOAD_FILE
        r"(\bINTO\s+DUMPFILE\b)",  # INTO DUMPFILE
        r"(\bSLEEP\s*\()",  # SLEEP function
        r"(\bBENCHMARK\s*\()",  # BENCHMARK function
        r"(\bEXTRACTVALUE\s*\()",  # EXTRACTVALUE function
        r"(\bUPDATEXML\s*\()",  # UPDATEXML function
        r"(\bCONCAT\s*\(.*SELECT\b)",  # CONCAT with SELECT
        r"(\bCHAR\s*\(\d+\))",  # CHAR function with numbers
        r"(\bASCII\s*\()",  # ASCII function
        r"(\bORD\s*\()",  # ORD function
        r"(\bHEX\s*\()",  # HEX function
        r"(\bUNHEX\s*\()",  # UNHEX function
        r"(\bCONVERT\s*\()",  # CONVERT function
        r"(\bCAST\s*\()",  # CAST function with suspicious patterns
        r"(\bSUBSTRING\s*\(.*SELECT\b)",  # SUBSTRING with SELECT
        r"(\bIF\s*\(.*SELECT\b)",  # IF with SELECT
        r"(\bCASE\s+WHEN\b.*SELECT\b)",  # CASE WHEN with SELECT
    ]
    
    # XSS patterns to detect
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"vbscript:",
        r"onload\s*=",
        r"onerror\s*=",
        r"onclick\s*=",
        r"onmouseover\s*=",
        r"onfocus\s*=",
        r"onblur\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"<form[^>]*>",
        r"<input[^>]*>",
        r"<textarea[^>]*>",
        r"<button[^>]*>",
    ]
    
    @classmethod
    def validate_input(cls, value: Any, field_name: str = "input") -> bool:
        """
        Validate input for SQL injection and XSS attempts
        
        Args:
            value: The input value to validate
            field_name: Name of the field being validated (for logging)
            
        Returns:
            bool: True if input is safe, False if potentially malicious
        """
        if value is None:
            return True
            
        # Convert to string for validation
        str_value = str(value).upper()
        
        # Check for dangerous keywords
        for keyword in cls.DANGEROUS_KEYWORDS:
            if keyword in str_value:
                logger.warning(f"Dangerous keyword '{keyword}' detected in {field_name}: {value}")
                return False
        
        # Check for SQL injection patterns
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, str_value, re.IGNORECASE):
                logger.warning(f"SQL injection pattern detected in {field_name}: {value}")
                return False
        
        # Check for XSS patterns
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, str(value), re.IGNORECASE):
                logger.warning(f"XSS pattern detected in {field_name}: {value}")
                return False
        
        return True
    
    @classmethod
    def sanitize_input(cls, value: Any) -> str:
        """
        Sanitize input by escaping HTML and removing dangerous characters
        
        Args:
            value: The input value to sanitize
            
        Returns:
            str: Sanitized string
        """
        if value is None:
            return ""
        
        # Convert to string and escape HTML
        sanitized = html.escape(str(value))
        
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        
        # Remove other control characters
        sanitized = re.sub(r'[\x01-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)
        
        return sanitized.strip()
    
    @classmethod
    def validate_sql_params(cls, params: tuple) -> bool:
        """
        Validate SQL parameters for injection attempts
        
        Args:
            params: Tuple of parameters to validate
            
        Returns:
            bool: True if all parameters are safe
        """
        if not params:
            return True
        
        for i, param in enumerate(params):
            if not cls.validate_input(param, f"param_{i}"):
                return False
        
        return True
    
    @classmethod
    def validate_json_data(cls, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate JSON data for injection attempts
        
        Args:
            data: Dictionary of data to validate
            
        Returns:
            Dict[str, List[str]]: Dictionary of field names and their validation errors
        """
        errors = {}
        
        if not isinstance(data, dict):
            return {"general": ["Invalid data format"]}
        
        for field_name, value in data.items():
            if not cls.validate_input(value, field_name):
                if field_name not in errors:
                    errors[field_name] = []
                errors[field_name].append("Contains potentially malicious content")
        
        return errors


def validate_request_data(required_fields: Optional[List[str]] = None, 
                         optional_fields: Optional[List[str]] = None):
    """
    Decorator to validate request data for SQL injection and XSS
    
    Args:
        required_fields: List of required field names
        optional_fields: List of optional field names
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Get JSON data from request
                data = request.get_json()
                
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                
                # Validate required fields
                if required_fields:
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        return jsonify({
                            'error': 'Missing required fields',
                            'missing_fields': missing_fields
                        }), 400
                
                # Validate all fields for security
                validator = SQLSecurityValidator()
                validation_errors = validator.validate_json_data(data)
                
                if validation_errors:
                    logger.warning(f"Security validation failed for {f.__name__}: {validation_errors}")
                    return jsonify({
                        'error': 'Invalid input detected',
                        'details': 'Input contains potentially malicious content'
                    }), 400
                
                # Sanitize input data
                sanitized_data = {}
                all_fields = (required_fields or []) + (optional_fields or [])
                
                for field in all_fields:
                    if field in data:
                        sanitized_data[field] = validator.sanitize_input(data[field])
                
                # Add sanitized data to request context
                request.sanitized_data = sanitized_data
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Error in request validation: {e}")
                return jsonify({'error': 'Request validation failed'}), 500
        
        return decorated_function
    return decorator


def secure_db_query(db, query: str, params: tuple = None, fetch: bool = True):
    """
    Secure database query execution with additional validation
    
    Args:
        db: Database connection instance
        query: SQL query string
        params: Query parameters
        fetch: Whether to fetch results
        
    Returns:
        Query results or execution status
    """
    try:
        # Validate query parameters
        if params and not SQLSecurityValidator.validate_sql_params(params):
            raise ValueError("Invalid parameters detected")
        
        # Log query for audit (without sensitive data)
        logger.info(f"Executing query: {query[:100]}...")
        
        # Execute query using the existing secure method
        result = db.execute_query(query, params, fetch)
        
        return result
        
    except Exception as e:
        logger.error(f"Secure query execution failed: {e}")
        raise


class SQLInjectionProtection:
    """
    SQL Injection Protection middleware
    """
    
    @staticmethod
    def validate_user_input(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize user input
        
        Args:
            data: Dictionary of user input data
            
        Returns:
            Dict[str, Any]: Sanitized data
        """
        validator = SQLSecurityValidator()
        sanitized_data = {}
        
        for key, value in data.items():
            if validator.validate_input(value, key):
                sanitized_data[key] = validator.sanitize_input(value)
            else:
                raise ValueError(f"Invalid input detected in field: {key}")
        
        return sanitized_data
    
    @staticmethod
    def create_safe_query(base_query: str, conditions: Dict[str, Any]) -> tuple:
        """
        Create a safe parameterized query from conditions
        
        Args:
            base_query: Base SQL query with WHERE clause
            conditions: Dictionary of conditions to add
            
        Returns:
            tuple: (query_string, parameters)
        """
        if not conditions:
            return base_query, ()
        
        where_clauses = []
        params = []
        
        for field, value in conditions.items():
            # Validate field name (should only contain alphanumeric and underscore)
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', field):$', field):
                raise ValueError(f"Invalid field name: {field}")
            
            where_clauses.append(f"{field} = %s")
            params.append(value)
        
        if where_clauses:
            if "WHERE" in base_query.upper():
                query = f"{base_query} AND {' AND '.join(where_clauses)}"
            else:
                query = f"{base_query} WHERE {' AND '.join(where_clauses)}"
        else:
            query = base_query
        
        return query, tuple(params)


# Security audit logging
def log_security_event(event_type: str, details: Dict[str, Any], user_id: Optional[str] = None):
    """
    Log security events for audit purposes
    
    Args:
        event_type: Type of security event
        details: Event details
        user_id: User ID if available
    """
    logger.warning(f"SECURITY EVENT: {event_type} | User: {user_id} | Details: {details}")


# Input validation decorators for specific data types
def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None$'
    return re.match(pattern, email) is not None


def validate_username(username: str) -> bool:
    """Validate username format (alphanumeric and underscore only)"""
    pattern = r'^[a-zA-Z0-9_]{3,50}$'
    return re.match(pattern, username) is not None$'
    return re.match(pattern, username) is not None


def validate_student_id(student_id: str) -> bool:
    """Validate student ID format"""
    pattern = r'^[A-Z]{3}[0-9]{3}$'  # Format: STU001
    return re.match(pattern, student_id) is not None$'  # Format: STU001
    return re.match(pattern, student_id) is not None


def validate_section_id(section_id: str) -> bool:
    """Validate section ID format"""
    pattern = r'^[A-Z]$'  # Single uppercase letter
    return re.match(pattern, section_id) is not None$'  # Single uppercase letter
    return re.match(pattern, section_id) is not None


def validate_course_name(course_name: str) -> bool:
    """Validate course name format"""
    pattern = r'^[a-zA-Z0-9\s\-_]{1,100}$'  # Alphanumeric, spaces, hyphens, underscores
    return re.match(pattern, course_name) is not None$'  # Alphanumeric, spaces, hyphens, underscores
    return re.match(pattern, course_name) is not None


# Comprehensive input validation function
def validate_attendance_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate attendance-specific data
    
    Args:
        data: Dictionary of attendance data
        
    Returns:
        Dict[str, List[str]]: Validation errors by field
    """
    errors = {}
    
    # Validate student_id
    if 'student_id' in data and not validate_student_id(data['student_id']):
        errors['student_id'] = ['Invalid student ID format']
    
    # Validate section_id
    if 'section_id' in data and not validate_section_id(data['section_id']):
        errors['section_id'] = ['Invalid section ID format']
    
    # Validate course_name
    if 'course_name' in data and not validate_course_name(data['course_name']):
        errors['course_name'] = ['Invalid course name format']
    
    # Validate status
    if 'status' in data and data['status'] not in ['present', 'absent']:
        errors['status'] = ['Status must be either "present" or "absent"']
    
    # Validate session_type
    if 'session_type' in data and data['session_type'] not in ['theory', 'lab']:
        errors['session_type'] = ['Session type must be either "theory" or "lab"']
    
    return errors
# Input validation decorators for specific data types
def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username: str) -> bool:
    """Validate username format (alphanumeric and underscore only)"""
    pattern = r'^[a-zA-Z0-9_]{3,50}$'
    return re.match(pattern, username) is not None


def validate_student_id(student_id: str) -> bool:
    """Validate student ID format"""
    pattern = r'^[A-Z]{3}[0-9]{3}$'  # Format: STU001
    return re.match(pattern, student_id) is not None


def validate_section_id(section_id: str) -> bool:
    """Validate section ID format"""
    pattern = r'^[A-Z]$'  # Single uppercase letter
    return re.match(pattern, section_id) is not None


def validate_course_name(course_name: str) -> bool:
    """Validate course name format"""
    pattern = r'^[a-zA-Z0-9\s\-_]{1,100}$'  # Alphanumeric, spaces, hyphens, underscores
    return re.match(pattern, course_name) is not None


# Comprehensive input validation function
def validate_attendance_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate attendance-specific data
    
    Args:
        data: Dictionary of attendance data
        
    Returns:
        Dict[str, List[str]]: Validation errors by field
    """
    errors = {}
    
    # Validate student_id
    if 'student_id' in data and not validate_student_id(data['student_id']):
        errors['student_id'] = ['Invalid student ID format']
    
    # Validate section_id
    if 'section_id' in data and not validate_section_id(data['section_id']):
        errors['section_id'] = ['Invalid section ID format']
    
    # Validate course_name
    if 'course_name' in data and not validate_course_name(data['course_name']):
        errors['course_name'] = ['Invalid course name format']
    
    # Validate status
    if 'status' in data and data['status'] not in ['present', 'absent']:
        errors['status'] = ['Status must be either "present" or "absent"']
    
    # Validate session_type
    if 'session_type' in data and data['session_type'] not in ['theory', 'lab']:
        errors['session_type'] = ['Session type must be either "theory" or "lab"']
    
    return errors