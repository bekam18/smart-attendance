import sys
sys.path.append('backend')
from db.mysql import get_db

db = get_db()

print("\n" + "="*60)
print("ALL USERS IN DATABASE")
print("="*60)

sql = 'SELECT id, username, name, role FROM users ORDER BY role, id'
users = db.execute_query(sql)

by_role = {}
for user in users:
    role = user['role']
    if role not in by_role:
        by_role[role] = []
    by_role[role].append(user)

for role, role_users in by_role.items():
    print(f"\n{role.upper()} ({len(role_users)} users):")
    for user in role_users:
        print(f"  - ID: {user['id']}, Username: {user['username']}, Name: {user['name']}")

print("\n" + "="*60)
