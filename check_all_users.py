import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Bekam@1818',
    database='smart_attendance'
)

cursor = conn.cursor(dictionary=True)
cursor.execute('SELECT id, username, role FROM users ORDER BY role, username')
users = cursor.fetchall()

print('All users in database:')
for u in users:
    print(f'  {u["username"]:15} ({u["role"]:12}) ID: {u["id"]}')

cursor.close()
conn.close()
