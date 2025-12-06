import sys
sys.path.insert(0, 'backend')

from db.mysql import get_db

db = get_db()

print("\n" + "="*60)
print("CHECKING SESSIONS TABLE")
print("="*60 + "\n")

# Check if sessions table exists
result = db.execute_query("SHOW TABLES LIKE 'sessions'")
if result:
    print("✅ Sessions table exists\n")
    
    # Get table structure
    schema = db.execute_query("DESCRIBE sessions")
    print("Sessions table columns:")
    for col in schema:
        print(f"  - {col['Field']:20} {col['Type']:20}")
    
    # Count records
    count = db.execute_query("SELECT COUNT(*) as count FROM sessions")
    print(f"\nTotal sessions: {count[0]['count']}")
    
    # Show sample
    if count[0]['count'] > 0:
        sample = db.execute_query("SELECT * FROM sessions LIMIT 3")
        print("\nSample sessions:")
        for s in sample:
            print(f"  ID: {s.get('id')}, Name: {s.get('session_name') or s.get('name')}, Course: {s.get('course_name')}")
else:
    print("❌ Sessions table does NOT exist")
    print("\nChecking attendance.session_id values...")
    result = db.execute_query("SELECT DISTINCT session_id FROM attendance LIMIT 10")
    print(f"Sample session_id values: {[r['session_id'] for r in result]}")

print("\n" + "="*60 + "\n")
