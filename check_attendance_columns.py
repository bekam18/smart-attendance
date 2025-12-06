import sys
sys.path.insert(0, 'backend')

from db.mysql import get_db

db = get_db()

# Get actual columns
result = db.execute_query("SELECT * FROM attendance LIMIT 1")

if result:
    print("\n" + "="*60)
    print("ACTUAL ATTENDANCE TABLE COLUMNS:")
    print("="*60)
    for key in result[0].keys():
        print(f"  - {key}")
    print("="*60 + "\n")
else:
    print("No records found, checking schema...")
    result = db.execute_query("DESCRIBE attendance")
    print("\n" + "="*60)
    print("ATTENDANCE TABLE SCHEMA:")
    print("="*60)
    for row in result:
        print(f"  - {row['Field']:20} {row['Type']:20}")
    print("="*60 + "\n")
