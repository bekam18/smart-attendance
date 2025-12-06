import sys
sys.path.insert(0, 'backend')

print("\n" + "="*60)
print("DIAGNOSING EXPORT ISSUE")
print("="*60 + "\n")

try:
    from db.mysql import get_db
    
    db = get_db()
    
    # Test 1: Check attendance table exists
    print("Test 1: Checking attendance table...")
    try:
        result = db.execute_query("SHOW TABLES LIKE 'attendance'")
        if result:
            print("✅ Attendance table exists")
        else:
            print("❌ Attendance table NOT found!")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error checking table: {e}")
        sys.exit(1)
    
    # Test 2: Check table structure
    print("\nTest 2: Checking table columns...")
    try:
        # Use a simpler query that doesn't cause issues
        result = db.execute_query("SELECT * FROM attendance LIMIT 0")
        print("✅ Table structure is accessible")
    except Exception as e:
        print(f"❌ Error accessing table: {e}")
    
    # Test 3: Count records
    print("\nTest 3: Counting records...")
    try:
        result = db.execute_query("SELECT COUNT(*) as count FROM attendance")
        count = result[0]['count'] if result else 0
        print(f"✅ Found {count} attendance records")
        
        if count == 0:
            print("⚠️  WARNING: No attendance records exist!")
            print("   The export will work but return an empty file.")
    except Exception as e:
        print(f"❌ Error counting records: {e}")
    
    # Test 4: Check students table
    print("\nTest 4: Checking students table...")
    try:
        result = db.execute_query("SELECT COUNT(*) as count FROM students")
        count = result[0]['count'] if result else 0
        print(f"✅ Found {count} students")
    except Exception as e:
        print(f"❌ Error checking students: {e}")
    
    # Test 5: Try the actual export query
    print("\nTest 5: Testing export query...")
    try:
        query = """
            SELECT 
                a.id,
                a.student_id,
                s.name as student_name,
                a.course_name,
                a.section_id,
                a.class_year,
                a.session_id,
                a.status,
                a.confidence,
                a.timestamp,
                a.date,
                a.instructor_id
            FROM attendance a
            LEFT JOIN students s ON a.student_id = s.student_id
            LIMIT 1
        """
        result = db.execute_query(query)
        if result:
            print("✅ Export query works!")
            print(f"   Sample record keys: {list(result[0].keys())}")
        else:
            print("⚠️  Query returned no results (but no error)")
    except Exception as e:
        print(f"❌ Export query failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 6: Test CSV generation
    print("\nTest 6: Testing CSV generation...")
    try:
        import csv
        from io import StringIO
        
        si = StringIO()
        writer = csv.writer(si)
        writer.writerow(['Test', 'CSV', 'Generation'])
        writer.writerow(['Value1', 'Value2', 'Value3'])
        output = si.getvalue()
        si.close()
        
        if output:
            print("✅ CSV generation works!")
            print(f"   Generated {len(output)} bytes")
        else:
            print("❌ CSV generation failed")
    except Exception as e:
        print(f"❌ CSV generation error: {e}")
    
    print("\n" + "="*60)
    print("DIAGNOSIS COMPLETE")
    print("="*60 + "\n")
    
    print("Summary:")
    print("- If all tests passed, the export should work")
    print("- If any test failed, check the error message above")
    print("- Restart backend and try export again")
    print()

except Exception as e:
    print(f"\n❌ FATAL ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
