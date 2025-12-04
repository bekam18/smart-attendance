import mysql.connector
import bcrypt

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Bekam@1818',
    database='smart_attendance'
)

cursor = conn.cursor()

# Reset password to 'password' for all instructors using bcrypt
new_password_hash = bcrypt.hashpw('password'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

cursor.execute(
    "UPDATE users SET password = %s WHERE role = 'instructor'",
    (new_password_hash,)
)

conn.commit()

print(f"✓ Reset password for {cursor.rowcount} instructors to 'password'")

cursor.close()
conn.close()
