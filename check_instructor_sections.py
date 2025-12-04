import mysql.connector
import json

# Connect to database
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Bekam@1818',
    database='smart_attendance'
)

cursor = conn.cursor(dictionary=True)

# Get instructor info
cursor.execute("SELECT id, username, sections, courses FROM users WHERE role = 'instructor'")
instructors = cursor.fetchall()

print("=== INSTRUCTOR SECTIONS ===\n")
for instructor in instructors:
    print(f"Instructor: {instructor['username']} (ID: {instructor['id']})")
    
    # Parse sections
    sections = []
    if instructor['sections']:
        try:
            sections = json.loads(instructor['sections'])
        except:
            sections = []
    
    # Parse courses
    courses = []
    if instructor['courses']:
        try:
            courses = json.loads(instructor['courses'])
        except:
            courses = []
    
    print(f"  Sections: {sections}")
    print(f"  Courses: {courses}")
    print()

cursor.close()
conn.close()
