import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Bekam@1818',
    database='smart_attendance'
)

cursor = conn.cursor(dictionary=True)

cursor.execute('''
    SELECT COUNT(*) as count, course_name, section_id 
    FROM attendance 
    WHERE date = '2025-12-04' 
    GROUP BY course_name, section_id
''')

results = cursor.fetchall()

print('Attendance for 2025-12-04:')
for r in results:
    print(f"  {r['course_name']} - Section {r['section_id']}: {r['count']} records")

cursor.close()
conn.close()
