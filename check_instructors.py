import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Bekam@1818',
    database='smart_attendance'
)

cursor = conn.cursor(dictionary=True)
cursor.execute('SELECT id, username, role FROM users WHERE role="instructor"')
users = cursor.fetchall()

print('Instructors in database:')
for u in users:
    print(f'  ID: {u["id"]}, Username: {u["username"]}')

cursor.close()
conn.close()
