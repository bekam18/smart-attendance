"""
Update sessions table status enum to support new session statuses:
- stopped_daily (can be reopened after 12 hours)
- ended_semester (permanent end)
- completed (legacy status)
"""
import mysql.connector

print("="*80)
print("UPDATING SESSIONS STATUS ENUM")
print("="*80)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Bekam@1818",
    database="smart_attendance"
)

cursor = db.cursor()

try:
    # Check current enum values
    cursor.execute("""
        SELECT COLUMN_TYPE 
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = 'smart_attendance' 
        AND TABLE_NAME = 'sessions' 
        AND COLUMN_NAME = 'status'
    """)
    result = cursor.fetchone()
    print(f"\n✓ Current status enum: {result[0]}")
    
    # Update enum to include new values
    print("\n→ Updating status enum to include new values...")
    cursor.execute("""
        ALTER TABLE sessions 
        MODIFY COLUMN status ENUM('active', 'ended', 'completed', 'stopped_daily', 'ended_semester') 
        DEFAULT 'active'
    """)
    db.commit()
    print("✅ Status enum updated successfully!")
    
    print("\n📝 New status values:")
    print("  - active: Session is currently running")
    print("  - stopped_daily: Session stopped for the day (can reopen after 12h)")
    print("  - ended_semester: Session ended permanently for semester")
    print("  - completed: Legacy status (same as ended)")
    print("  - ended: Legacy status (kept for compatibility)")
    
    # Verify update
    print("\n" + "="*80)
    print("VERIFYING UPDATE")
    print("="*80)
    cursor.execute("""
        SELECT COLUMN_TYPE 
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = 'smart_attendance' 
        AND TABLE_NAME = 'sessions' 
        AND COLUMN_NAME = 'status'
    """)
    result = cursor.fetchone()
    print(f"✅ Updated status enum: {result[0]}")
    
    # Check if any sessions need status migration
    print("\n" + "="*80)
    print("CHECKING EXISTING SESSIONS")
    print("="*80)
    cursor.execute("SELECT id, name, status FROM sessions ORDER BY start_time DESC LIMIT 10")
    sessions = cursor.fetchall()
    
    if sessions:
        print(f"\nFound {len(sessions)} recent sessions:")
        for session in sessions:
            print(f"  - ID: {session[0]}, Name: {session[1]}, Status: {session[2]}")
    else:
        print("\nNo sessions found")

except Exception as e:
    print(f"\n❌ Error: {e}")
    db.rollback()
finally:
    cursor.close()
    db.close()

print("\n" + "="*80)
print("MIGRATION COMPLETE")
print("="*80)
print("\n✅ Sessions table now supports:")
print("  - active (running)")
print("  - stopped_daily (can reopen)")
print("  - ended_semester (permanent)")
print("  - completed (legacy)")
print("  - ended (legacy)")
