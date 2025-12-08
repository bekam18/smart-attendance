import mysql.connector
from mysql.connector import Error, pooling
import os
import sys
from datetime import datetime
import json

class MySQLConnection:
    def __init__(self):
        self.pool = None
        self.init_pool()
    
    def init_pool(self):
        """Initialize MySQL connection pool"""
        try:
            from config import Config as config
            
            self.pool = pooling.MySQLConnectionPool(
                pool_name="smartattendance_pool",
                pool_size=5,
                host=config.MYSQL_HOST,
                port=config.MYSQL_PORT,
                database=config.MYSQL_DATABASE,
                user=config.MYSQL_USER,
                password=config.MYSQL_PASSWORD,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci',
                autocommit=False
            )
            
            # Test connection
            conn = self.pool.get_connection()
            if conn.is_connected():
                print(f"✅ Connected to MySQL: {config.MYSQL_DATABASE}")
                conn.close()
                return True
                
        except Error as e:
            print(f"❌ MySQL connection failed: {e}")
            sys.exit(1)
    
    def get_connection(self):
        """Get connection from pool"""
        try:
            return self.pool.get_connection()
        except Error as e:
            print(f"❌ Error getting connection: {e}")
            raise
    
    def execute_query(self, query, params=None, fetch=True):
        """Execute a query and return results"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True, buffered=True)  # Added buffered=True
            
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith('SELECT') or query.strip().upper().startswith('SHOW') or query.strip().upper().startswith('DESCRIBE'):
                result = cursor.fetchall()
                return result
            else:
                conn.commit()
                return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
                
        except Error as e:
            if conn:
                conn.rollback()
            print(f"❌ Query execution error: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def execute_many(self, query, data_list):
        """Execute query with multiple data sets"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.executemany(query, data_list)
            conn.commit()
            return cursor.rowcount
            
        except Error as e:
            if conn:
                conn.rollback()
            print(f"❌ Batch execution error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

# Global MySQL connection instance
mysql_db = MySQLConnection()

def get_db():
    """Get MySQL database connection instance"""
    return mysql_db

def init_db():
    """Initialize MySQL database (already done via connection pool)"""
    return mysql_db
