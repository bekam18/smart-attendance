"""
Reset student password
"""

import mysql.connector
import bcrypt

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Bekam@1818',
    database='smart_attendance'
)

cursor = conn.cursor()

# Hash new password
new_password = 'student123'
hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Update password
cursor.execute("UPDATE users SET password = %s WHERE username = 'STU001'", (hashed,))
conn.commit()

print(f"✅ Password for STU001 reset to: {new_password}")

cursor.close()
conn.close()
