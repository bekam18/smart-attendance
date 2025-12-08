"""
Test individual regex patterns to find the problematic one
"""

import re

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

def test_patterns():
    test_string = "admin"
    
    print("Testing SQL patterns:")
    for i, pattern in enumerate(SQL_PATTERNS):
        try:
            result = re.search(pattern, test_string, re.IGNORECASE)
            print(f"  Pattern {i+1}: {pattern} - OK")
        except Exception as e:
            print(f"  Pattern {i+1}: {pattern} - ERROR: {e}")
    
    print("\nTesting XSS patterns:")
    for i, pattern in enumerate(XSS_PATTERNS):
        try:
            result = re.search(pattern, test_string, re.IGNORECASE)
            print(f"  Pattern {i+1}: {pattern} - OK")
        except Exception as e:
            print(f"  Pattern {i+1}: {pattern} - ERROR: {e}")

if __name__ == "__main__":
    test_patterns()