import sys
sys.path.insert(0, 'backend')

from db.mysql import get_db

db = get_db()
result = db.execute_query('DESCRIBE attendance')

print('\n' + '='*50)
print('ATTENDANCE TABLE COLUMNS')
print('='*50)
for r in result:
    print(f"  {r['Field']:20} {r['Type']:20} {r['Null']:5} {r['Key']:5}")
print('='*50 + '\n')

# Check if there are any records
count = db.execute_query('SELECT COUNT(*) as count FROM attendance')
print(f"Total attendance records: {count[0]['count']}")

# Show sample record if exists
if count[0]['count'] > 0:
    sample = db.execute_query('SELECT * FROM attendance LIMIT 1')
    print('\nSample record columns:')
    for key in sample[0].keys():
        print(f"  - {key}")
