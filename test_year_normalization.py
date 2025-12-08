"""
Test year normalization logic
"""

student_year = "4"
year_normalized = student_year.replace('th Year', '').replace('st Year', '').replace('nd Year', '').replace('rd Year', '').strip()

print(f"Original: '{student_year}'")
print(f"Normalized: '{year_normalized}'")

student_year2 = "4th Year"
year_normalized2 = student_year2.replace('th Year', '').replace('st Year', '').replace('nd Year', '').replace('rd Year', '').strip()

print(f"\nOriginal: '{student_year2}'")
print(f"Normalized: '{year_normalized2}'")

# Test query
import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Bekam@1818',
    database='smart_attendance'
)

cursor = conn.cursor(dictionary=True)

# Test with STU002 (year = "4")
cursor.execute("SELECT year, section FROM students WHERE student_id = 'STU002'")
student = cursor.fetchone()
print(f"\nStudent STU002: Year='{student['year']}', Section='{student['section']}'")

year_normalized = student['year'].replace('th Year', '').replace('st Year', '').replace('nd Year', '').replace('rd Year', '').strip()
print(f"Normalized year: '{year_normalized}'")

# Query sessions
cursor.execute("""
    SELECT DISTINCT course_name, year, section_id
    FROM sessions 
    WHERE (year = %s OR year = %s) AND section_id = %s
""", (student['year'], year_normalized, student['section']))

sessions = cursor.fetchall()
print(f"\nFound {len(sessions)} sessions:")
for s in sessions:
    print(f"  - {s['course_name']} (Year: {s['year']}, Section: {s['section_id']})")

cursor.close()
conn.close()
