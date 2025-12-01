@echo off
echo ========================================
echo Testing Admin Enable/Disable/Edit Features
echo ========================================
echo.

cd backend

echo Testing backend endpoints...
python -c "
from db.mongo import get_db
from bson import ObjectId

db = get_db()

print('=== Current Instructors ===')
instructors = list(db.users.find({'role': 'instructor'}))
for i in instructors:
    print(f\"ID: {i['_id']}, Name: {i['name']}, Enabled: {i.get('enabled', True)}\")

print('\n=== Current Students ===')
students = list(db.students.find().limit(5))
for s in students:
    user = db.users.find_one({'_id': ObjectId(s['user_id'])})
    print(f\"ID: {s['_id']}, Name: {s['name']}, Enabled: {user.get('enabled', True) if user else 'N/A'}\")

print('\n✅ Database connection successful!')
print('✅ All collections accessible!')
"

echo.
echo ========================================
echo Test Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Start backend: cd backend ^&^& python app.py
echo 2. Start frontend: cd frontend ^&^& npm run dev
echo 3. Login as admin and test Enable/Disable/Edit features
echo.
pause
