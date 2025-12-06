import sys
sys.path.insert(0, 'backend')

print("\n" + "="*60)
print("TESTING EXCEL EXPORT")
print("="*60 + "\n")

# Test 1: Check pandas
print("Test 1: Checking pandas...")
try:
    import pandas as pd
    print(f"✅ pandas installed: version {pd.__version__}")
except ImportError as e:
    print(f"❌ pandas not installed: {e}")
    print("   Run: pip install pandas")
    sys.exit(1)

# Test 2: Check openpyxl
print("\nTest 2: Checking openpyxl...")
try:
    import openpyxl
    print(f"✅ openpyxl installed: version {openpyxl.__version__}")
except ImportError as e:
    print(f"❌ openpyxl not installed: {e}")
    print("   Run: pip install openpyxl")
    sys.exit(1)

# Test 3: Test Excel generation
print("\nTest 3: Testing Excel generation...")
try:
    from io import BytesIO
    
    # Create sample data
    df = pd.DataFrame({
        'ID': [1, 2, 3],
        'Name': ['Test1', 'Test2', 'Test3'],
        'Value': [100, 200, 300]
    })
    
    # Create Excel in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Test')
    
    output.seek(0)
    size = output.getbuffer().nbytes
    
    print(f"✅ Excel generation works! ({size} bytes)")
    
except Exception as e:
    print(f"❌ Excel generation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test actual export query
print("\nTest 4: Testing actual export with real data...")
try:
    from db.mysql import get_db
    
    db = get_db()
    
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
        LIMIT 5
    """
    
    records = db.execute_query(query)
    print(f"✅ Query returned {len(records)} records")
    
    # Convert to DataFrame
    df = pd.DataFrame(records)
    print(f"✅ DataFrame created with {len(df)} rows, {len(df.columns)} columns")
    
    # Rename columns
    df = df.rename(columns={
        'id': 'ID',
        'student_id': 'Student ID',
        'student_name': 'Student Name',
        'course_name': 'Course',
        'section_id': 'Section',
        'class_year': 'Year',
        'session_id': 'Session ID',
        'status': 'Status',
        'confidence': 'Confidence',
        'date': 'Date',
        'timestamp': 'Timestamp',
        'instructor_id': 'Instructor ID'
    })
    
    # Format confidence
    if 'Confidence' in df.columns:
        df['Confidence'] = df['Confidence'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else 'N/A')
    
    # Fill NaN
    df = df.fillna('N/A')
    
    print(f"✅ DataFrame formatted successfully")
    
    # Create Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance Records')
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Attendance Records']
        for idx, col in enumerate(df.columns):
            try:
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                ) + 2
                col_letter = chr(65 + idx) if idx < 26 else chr(65 + idx // 26 - 1) + chr(65 + idx % 26)
                worksheet.column_dimensions[col_letter].width = min(max_length, 50)
            except:
                pass
    
    output.seek(0)
    size = output.getbuffer().nbytes
    
    print(f"✅ Excel file generated successfully! ({size} bytes)")
    
    # Save test file
    with open('test_export.xlsx', 'wb') as f:
        f.write(output.read())
    
    print(f"✅ Test file saved: test_export.xlsx")
    
except Exception as e:
    print(f"❌ Export test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("ALL TESTS PASSED!")
print("="*60)
print("\nExcel export should work now.")
print("If it still fails, check the backend console for the exact error.")
print()
