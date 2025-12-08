"""Check attendance table unique constraints"""
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Bekam@1818",
    database="smart_attendance"
)

cursor = db.cursor(dictionary=True)

# Check table structure
cursor.execute("SHOW CREATE TABLE attendance")
result = cursor.fetchone()
print("="*80)
print("ATTENDANCE TABLE STRUCTURE")
print("="*80)
print(result['Create Table'])

print("\n" + "="*80)
print("INDEXES ON ATTENDANCE TABLE")
print("="*80)
cursor.execute("SHOW INDEX FROM attendance")
indexes = cursor.fetchall()
for idx in indexes:
    print(f"Key: {idx['Key_name']}, Column: {idx['Column_name']}, Unique: {idx['Non_unique'] == 0}")

cursor.close()
db.close()
