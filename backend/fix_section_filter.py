"""
Fix section_id filter in instructor.py export functions
"""

import re

# Read the file
import os
file_path = os.path.join(os.path.dirname(__file__), 'blueprints', 'instructor.py')
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to find the filter sections in export functions
# We need to add section_id after session_id in two places

# Fix 1: Add section_id to the "Get same filters" section
pattern1 = r"(# Get same filters\s+start_date = request\.args\.get\('start_date'\)\s+end_date = request\.args\.get\('end_date'\)\s+student_id = request\.args\.get\('student_id'\)\s+session_id = request\.args\.get\('session_id'\))"
replacement1 = r"\1\n        section_id = request.args.get('section_id')"

content = re.sub(pattern1, replacement1, content)

# Fix 2: Add section_id filter to SQL query building (after session_id check)
pattern2 = r"(if session_id:\s+sql \+= ' AND session_id = %s'\s+params\.append\(session_id\))\s+(sql \+= ' ORDER BY)"
replacement2 = r"\1\n        \n        if section_id:\n            sql += ' AND section_id = %s'\n            params.append(section_id)\n        \n        \2"

content = re.sub(pattern2, replacement2, content)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Added section_id filter to export functions")
print("✓ CSV export function updated")
print("✓ Excel export function updated")
