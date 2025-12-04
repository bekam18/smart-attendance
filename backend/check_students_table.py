from db.mysql import get_db

db = get_db()
result = db.execute_query('DESCRIBE students')
print("\nStudents table structure:")
for r in result:
    print(f"  {r['Field']}: {r['Type']}")
