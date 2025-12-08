"""
Test individual regex patterns in sql_security.py
"""

import re

# SQL injection patterns from sql_security.py
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

def test_patterns():
    test_string = "admin"
    
    print("Testing SQL injection patterns:")
    for i, pattern in enumerate(SQL_INJECTION_PATTERNS):
        try:
            result = re.search(pattern, test_string, re.IGNORECASE)
            print(f"  Pattern {i+1}: OK")
        except Exception as e:
            print(f"  Pattern {i+1}: ERROR - {e}")
            print(f"    Pattern: {pattern}")

if __name__ == "__main__":
    test_patterns()