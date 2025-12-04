import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Bekam@1818',
    database='smart_attendance'
)

cursor = conn.cursor(dictionary=True)

cursor.execute('''
    SELECT COUNT(*) as count, course_name, section_id, date 
    FROM attendance 
    WHERE date = CURDATE() 
    GROUP BY course_name, section_id, date
''')

results = cursor.fetchall()

print('Attendance records for today:')
if results:
    for r in results:
        print(f"  {r['course_name']} - Section {r['section_id']}: {r['count']} records on {r['date']}")
else:
    print("  No records for today")
    
    # Check most recent date
    cursor.execute('SELECT DISTINCT date FROM attendance ORDER BY date DESC LIMIT 1')
    recent = cursor.fetchone()
    if recent:
        print(f"\nMost recent attendance date: {recent['date']}")

cursor.close()
conn.close()
