#!/usr/bin/env python3
"""
Quick fix script to remove MongoDB imports from remaining blueprint files
This allows the backend to start while you complete the full MySQL conversion
"""

import os
import re

files_to_fix = [
    'backend/blueprints/admin.py',
    'backend/blueprints/students.py',
    'backend/blueprints/attendance.py',
    'backend/blueprints/instructor.py',
    'backend/blueprints/debug.py'
]

def fix_file(filepath):
    """Remove MongoDB imports and change to MySQL imports"""
    if not os.path.exists(filepath):
        print(f"⚠️  File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Remove bson import
    content = re.sub(r'from bson import ObjectId\n?', '', content)
    
    # Change mongo import to mysql
    content = content.replace('from db.mongo import get_db', 'from db.mysql import get_db')
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed: {filepath}")
        return True
    else:
        print(f"ℹ️  No changes needed: {filepath}")
        return False

def main():
    print("="*60)
    print("Fixing MongoDB imports in blueprint files")
    print("="*60)
    print()
    
    fixed_count = 0
    for filepath in files_to_fix:
        if fix_file(filepath):
            fixed_count += 1
    
    print()
    print("="*60)
    print(f"Fixed {fixed_count}/{len(files_to_fix)} files")
    print("="*60)
    print()
    print("⚠️  NOTE: These files still need full MySQL query conversion!")
    print("The imports are fixed so the backend can start, but the")
    print("MongoDB queries inside need to be converted to MySQL.")
    print()
    print("See COMPLETE_MYSQL_MIGRATION.md for conversion guide.")
    print()
    print("Try starting the backend now:")
    print("  cd backend")
    print("  python app.py")

if __name__ == '__main__':
    main()
