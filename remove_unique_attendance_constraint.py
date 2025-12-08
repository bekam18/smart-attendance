"""
Remove unique_attendance constraint to allow multiple attendance records
when sessions are reopened (12-hour retake feature)
"""
import mysql.connector

print("="*80)
print("REMOVING UNIQUE ATTENDANCE CONSTRAINT")
print("="*80)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Bekam@1818",
    database="smart_attendance"
)

cursor = db.cursor()

try:
    # Check if constraint exists
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM information_schema.statistics
        WHERE table_schema = 'smart_attendance'
        AND table_name = 'attendance'
        AND index_name = 'unique_attendance'
    """)
    result = cursor.fetchone()
    
    if result[0] > 0:
        print("\n✓ Found unique_attendance constraint")
        
        # Drop the unique constraint
        print("\n→ Dropping unique_attendance constraint...")
        cursor.execute("ALTER TABLE attendance DROP INDEX unique_attendance")
        db.commit()
        print("✅ Constraint removed successfully!")
        
        print("\n📝 Reason: This constraint prevented students from being marked")
        print("   multiple times on the same day when sessions are reopened")
        print("   (12-hour retake feature).")
        
        print("\n✅ Now students can be marked present/absent multiple times")
        print("   when instructor reopens sessions after 12 hours.")
        
    else:
        print("\n⚠️ Constraint 'unique_attendance' not found - already removed?")
    
    # Verify removal
    print("\n" + "="*80)
    print("VERIFYING REMOVAL")
    print("="*80)
    cursor.execute("SHOW INDEX FROM attendance")
    indexes = cursor.fetchall()
    
    unique_found = False
    for idx in indexes:
        if idx[2] == 'unique_attendance':
            unique_found = True
            break
    
    if not unique_found:
        print("✅ Verified: unique_attendance constraint has been removed")
    else:
        print("❌ Error: Constraint still exists!")
    
    print("\n" + "="*80)
    print("CURRENT INDEXES")
    print("="*80)
    cursor.execute("SHOW INDEX FROM attendance")
    indexes = cursor.fetchall()
    for idx in indexes:
        print(f"Key: {idx[2]}, Column: {idx[4]}, Unique: {idx[1] == 0}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    db.rollback()
finally:
    cursor.close()
    db.close()

print("\n" + "="*80)
print("MIGRATION COMPLETE")
print("="*80)
