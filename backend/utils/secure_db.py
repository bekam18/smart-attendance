"""
Secure Database Wrapper for Smart Attendance System
Provides additional security layers on top of the existing MySQL connection
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from db.mysql import get_db
# from utils.sql_security import SQLSecurityValidator, log_security_event
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class SecureDatabase:
    """
    Secure database wrapper with built-in SQL injection protection
    """
    
    def __init__(self):
        self.db = get_db()
        # self.validator = SQLSecurityValidator()
    
    def execute_secure_query(self, query: str, params: Optional[Tuple] = None, 
                           fetch: bool = True, user_id: Optional[str] = None) -> Any:
        """
        Execute a database query with security validation
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch: Whether to fetch results
            user_id: User ID for audit logging
            
        Returns:
            Query results or execution status
        """
        try:
            # Validate query structure
            if not self._is_safe_query(query):
                log_security_event("UNSAFE_QUERY", {"query": query[:100]}, user_id)
                raise ValueError("Unsafe query detected")
            
            # Validate parameters
            if params and not self.validator.validate_sql_params(params):
                log_security_event("INVALID_PARAMS", {"params_count": len(params)}, user_id)
                raise ValueError("Invalid parameters detected")
            
            # Log query execution for audit
            self._log_query_execution(query, params, user_id)
            
            # Execute query using the existing secure method
            result = self.db.execute_query(query, params, fetch)
            
            return result
            
        except Exception as e:
            logger.error(f"Secure query execution failed: {e}")
            log_security_event("QUERY_EXECUTION_ERROR", {"error": str(e)}, user_id)
            raise
    
    def _is_safe_query(self, query: str) -> bool:
        """
        Validate that the query structure is safe
        
        Args:
            query: SQL query string
            
        Returns:
            bool: True if query is safe
        """
        # Remove extra whitespace and convert to uppercase for analysis
        clean_query = re.sub(r'\s+', ' ', query.strip().upper())
        
        # Allow only specific query types
        allowed_patterns = [
            r'^SELECT\s+',
            r'^INSERT\s+INTO\s+',
            r'^UPDATE\s+\w+\s+SET\s+',
            r'^DELETE\s+FROM\s+',
            r'^SHOW\s+',
            r'^DESCRIBE\s+',
            r'^EXPLAIN\s+'
        ]
        
        # Check if query matches allowed patterns
        for pattern in allowed_patterns:
            if re.match(pattern, clean_query):
                break
        else:
            logger.warning(f"Query doesn't match allowed patterns: {clean_query[:100]}")
            return False
        
        # Check for dangerous patterns
        dangerous_patterns = [
            r';\s*(DROP|DELETE|TRUNCATE|ALTER|CREATE)',  # Multiple statements
            r'UNION\s+SELECT',  # UNION attacks
            r'INTO\s+OUTFILE',  # File operations
            r'LOAD_FILE\s*\(',  # File reading
            r'BENCHMARK\s*\(',  # Time-based attacks
            r'SLEEP\s*\(',  # Time delays
            r'--\s*[^\r\n]*',  # SQL comments (potential bypass)
            r'/\*.*?\*/',  # Block comments
            r'EXEC\s*\(',  # Command execution
            r'EXECUTE\s*\(',  # Command execution
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, clean_query):
                logger.warning(f"Dangerous pattern detected: {pattern}")
                return False
        
        return True
    
    def _log_query_execution(self, query: str, params: Optional[Tuple], user_id: Optional[str]):
        """
        Log query execution for audit purposes
        
        Args:
            query: SQL query string
            params: Query parameters
            user_id: User ID for audit logging
        """
        # Log query type and table (without sensitive data)
        query_type = query.strip().split()[0].upper()
        
        # Extract table name
        table_match = re.search(r'(?:FROM|INTO|UPDATE|JOIN)\s+(\w+)', query.upper())
        table_name = table_match.group(1) if table_match else "unknown"
        
        logger.info(f"DB_QUERY: {query_type} on {table_name} | User: {user_id}")
    
    # Secure methods for common operations
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Securely get user by ID"""
        result = self.execute_secure_query(
            "SELECT * FROM users WHERE id = %s",
            (user_id,),
            user_id=str(user_id)
        )
        return result[0] if result else None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Securely get user by username"""
        if not self.validator.validate_input(username, "username"):
            raise ValueError("Invalid username format")
        
        result = self.execute_secure_query(
            "SELECT * FROM users WHERE username = %s",
            (username,)
        )
        return result[0] if result else None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Securely get user by email"""
        if not self.validator.validate_input(email, "email"):
            raise ValueError("Invalid email format")
        
        result = self.execute_secure_query(
            "SELECT * FROM users WHERE email = %s",
            (email,)
        )
        return result[0] if result else None
    
    def create_user(self, user_data: Dict[str, Any], created_by: Optional[str] = None) -> int:
        """Securely create a new user"""
        # Validate all input data
        validation_errors = self.validator.validate_json_data(user_data)
        if validation_errors:
            raise ValueError(f"Invalid user data: {validation_errors}")
        
        # Required fields
        required_fields = ['username', 'password', 'email', 'name', 'role']
        for field in required_fields:
            if field not in user_data:
                raise ValueError(f"Missing required field: {field}")
        
        query = '''
            INSERT INTO users (username, password, email, name, role, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        '''
        
        user_id = self.execute_secure_query(
            query,
            (
                user_data['username'],
                user_data['password'],  # Should already be hashed
                user_data['email'],
                user_data['name'],
                user_data['role'],
                datetime.utcnow()
            ),
            fetch=False,
            user_id=created_by
        )
        
        log_security_event("USER_CREATED", {
            "new_user_id": user_id,
            "role": user_data['role']
        }, created_by)
        
        return user_id
    
    def update_user(self, user_id: int, update_data: Dict[str, Any], 
                   updated_by: Optional[str] = None) -> bool:
        """Securely update user data"""
        # Validate input data
        validation_errors = self.validator.validate_json_data(update_data)
        if validation_errors:
            raise ValueError(f"Invalid update data: {validation_errors}")
        
        # Build dynamic update query
        set_clauses = []
        params = []
        
        allowed_fields = ['username', 'email', 'name', 'password', 'enabled']
        
        for field, value in update_data.items():
            if field in allowed_fields:
                set_clauses.append(f"{field} = %s")
                params.append(value)
        
        if not set_clauses:
            raise ValueError("No valid fields to update")
        
        params.append(user_id)
        
        query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = %s"
        
        result = self.execute_secure_query(
            query,
            tuple(params),
            fetch=False,
            user_id=updated_by
        )
        
        log_security_event("USER_UPDATED", {
            "target_user_id": user_id,
            "fields_updated": list(update_data.keys())
        }, updated_by)
        
        return result > 0
    
    def get_attendance_records(self, filters: Dict[str, Any], 
                             user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Securely get attendance records with filters"""
        # Validate filters
        validation_errors = self.validator.validate_json_data(filters)
        if validation_errors:
            raise ValueError(f"Invalid filters: {validation_errors}")
        
        # Build query with safe filters
        base_query = "SELECT * FROM attendance WHERE 1=1"
        params = []
        
        # Allowed filter fields
        allowed_filters = {
            'student_id': 'student_id = %s',
            'course_name': 'course_name = %s',
            'section_id': 'section_id = %s',
            'session_id': 'session_id = %s',
            'instructor_id': 'instructor_id = %s',
            'date': 'date = %s',
            'status': 'status = %s'
        }
        
        for field, value in filters.items():
            if field in allowed_filters and value is not None:
                base_query += f" AND {allowed_filters[field]}"
                params.append(value)
        
        base_query += " ORDER BY date DESC, timestamp DESC LIMIT 1000"
        
        return self.execute_secure_query(base_query, tuple(params), user_id=user_id)
    
    def create_attendance_record(self, attendance_data: Dict[str, Any], 
                               created_by: Optional[str] = None) -> int:
        """Securely create attendance record"""
        # Validate attendance data
        from utils.sql_security import validate_attendance_data
        validation_errors = validate_attendance_data(attendance_data)
        if validation_errors:
            raise ValueError(f"Invalid attendance data: {validation_errors}")
        
        # Additional validation
        general_errors = self.validator.validate_json_data(attendance_data)
        if general_errors:
            raise ValueError(f"Invalid input data: {general_errors}")
        
        query = '''
            INSERT INTO attendance (student_id, session_id, course_name, section_id, 
                                  session_type, status, confidence, instructor_id, date, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        
        record_id = self.execute_secure_query(
            query,
            (
                attendance_data['student_id'],
                attendance_data['session_id'],
                attendance_data['course_name'],
                attendance_data['section_id'],
                attendance_data['session_type'],
                attendance_data['status'],
                attendance_data.get('confidence', 0.0),
                attendance_data['instructor_id'],
                attendance_data['date'],
                attendance_data.get('timestamp', datetime.utcnow())
            ),
            fetch=False,
            user_id=created_by
        )
        
        log_security_event("ATTENDANCE_RECORDED", {
            "student_id": attendance_data['student_id'],
            "status": attendance_data['status']
        }, created_by)
        
        return record_id
    
    def get_students_by_section(self, section_id: str, 
                              user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Securely get students by section"""
        if not self.validator.validate_input(section_id, "section_id"):
            raise ValueError("Invalid section ID")
        
        return self.execute_secure_query(
            "SELECT * FROM students WHERE section = %s ORDER BY name",
            (section_id,),
            user_id=user_id
        )
    
    def check_duplicate_attendance(self, student_id: str, session_id: int, 
                                 user_id: Optional[str] = None) -> bool:
        """Check if attendance already exists for student in session"""
        if not self.validator.validate_input(student_id, "student_id"):
            raise ValueError("Invalid student ID")
        
        result = self.execute_secure_query(
            "SELECT id FROM attendance WHERE student_id = %s AND session_id = %s",
            (student_id, session_id),
            user_id=user_id
        )
        
        return len(result) > 0


# Global secure database instance
secure_db = SecureDatabase()

def get_secure_db() -> SecureDatabase:
    """Get secure database instance"""
    return secure_db