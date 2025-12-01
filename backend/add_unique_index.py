"""
Add unique index to attendance collection to prevent duplicates
This ensures one student = one attendance entry per session at database level
"""

from db.mongo import get_db
from pymongo.errors import DuplicateKeyError

def add_unique_index():
    """Add unique compound index on (student_id, session_id, date)"""
    
    db = get_db()
    
    print("="*80)
    print("ADDING UNIQUE INDEX TO ATTENDANCE COLLECTION")
    print("="*80)
    
    try:
        # Create unique compound index
        result = db.attendance.create_index(
            [
                ('student_id', 1),
                ('session_id', 1),
                ('date', 1)
            ],
            unique=True,
            name='unique_attendance_per_session'
        )
        
        print(f"\n✅ Index created: {result}")
        print(f"\n📋 Index details:")
        print(f"   Name: unique_attendance_per_session")
        print(f"   Fields: student_id + session_id + date")
        print(f"   Unique: True")
        print(f"\n✅ This prevents duplicate attendance entries at database level!")
        
    except Exception as e:
        if 'duplicate key' in str(e).lower():
            print(f"\n⚠️  ERROR: Duplicate records exist in database!")
            print(f"   Please run cleanup_duplicates.bat first to remove duplicates")
            print(f"   Then run this script again to add the unique index")
        else:
            print(f"\n❌ Error creating index: {e}")
            raise
    
    # List all indexes
    print(f"\n📋 All indexes on attendance collection:")
    indexes = db.attendance.list_indexes()
    for idx in indexes:
        print(f"   - {idx['name']}: {idx.get('key', {})}")
    
    print("\n" + "="*80)


if __name__ == '__main__':
    add_unique_index()
