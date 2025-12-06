import sys
sys.path.append('backend')
from db.mysql import get_db
from utils.security import verify_password

db = get_db()

print("\n" + "="*60)
print("CHECKING USER CREDENTIALS")
print("="*60)

# Get instructor users
sql = 'SELECT id, username, name, password FROM users WHERE role = "instructor"'
users = db.execute_query(sql)

print("\nInstructor users:")
for user in users:
    print(f"\n  Username: {user['username']}")
    print(f"  Name: {user['name']}")
    print(f"  ID: {user['id']}")
    
    # Try common passwords
    test_passwords = ['bacha123', 'bacha', '123456', 'password', 'beki123', 'beki']
    for pwd in test_passwords:
        if verify_password(pwd, user['password']):
            print(f"  ✅ Password: {pwd}")
            break
    else:
        print(f"  ⚠️  Password: (not in common list)")

print("\n" + "="*60)
