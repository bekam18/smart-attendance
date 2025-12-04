import mysql.connector
from datetime import datetime

# Connect to database
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Bekam@1818',
    database='smart_attendance'
)

cursor = conn.cursor(dictionary=True)

# Test parameters
section_id = 'A'
course_name = 'AI'
start_date = '2025-03-12'
end_date = '2025-03-12'

print("=== TESTING REPORT GENERATION ===\n")
print(f"Section: {section_id}")
print(f"Course: {course_name}")
print(f"Date Range: {start_date} to {end_date}\n")

# Get attendance records
sql = '''
    SELECT * FROM attendance 
    WHERE section_id = %s 
    AND course_name = %s 
    AND date >= %s 
    AND date <= %s
    ORDER BY date, timestamp
'''

cursor.execute(sql, (section_id, course_name, start_date, end_date))
records = cursor.fetchall()

print(f"Found {len(records)} attendance records\n")

if len(records) > 0:
    print("Sample records:")
    for i, record in enumerate(records[:5]):
        print(f"  {i+1}. Student: {record['student_id']}, Status: {record['status']}, Date: {record['date']}")
else:
    print("No attendance records found!")
    print("\nChecking what data exists...")
    
    # Check sections
    cursor.execute("SELECT DISTINCT section_id FROM attendance")
    sections = cursor.fetchall()
    print(f"Available sections in attendance: {[s['section_id'] for s in sections]}")
    
    # Check courses
    cursor.execute("SELECT DISTINCT course_name FROM attendance")
    courses = cursor.fetchall()
    print(f"Available courses in attendance: {[c['course_name'] for c in courses]}")
    
    # Check dates
    cursor.execute("SELECT DISTINCT date FROM attendance ORDER BY date DESC LIMIT 5")
    dates = cursor.fetchall()
    print(f"Recent dates in attendance: {[str(d['date']) for d in dates]}")

# Get students in section
cursor.execute("SELECT * FROM students WHERE section = %s", (section_id,))
students = cursor.fetchall()
print(f"\nFound {len(students)} students in section {section_id}")

cursor.close()
conn.close()
