@echo off
echo Checking students in database...
cd backend
python -c "from db.mongo import get_db; db = get_db(); students = list(db.students.find({}, {'student_id': 1, 'name': 1, 'section': 1, 'year': 1}).limit(15)); print('\nStudents in database:'); print('='*80); [print(f\"{s.get('student_id', 'NO_ID'):10} | {s.get('name', 'NO_NAME'):25} | Section: {s.get('section', 'MISSING'):5} | Year: {s.get('year', 'MISSING')}\") for s in students]; print('='*80); print(f'\nTotal students: {db.students.count_documents({})}'); section_a = db.students.count_documents({'section': 'A', 'year': '4th Year'}); print(f'Students in Section A, 4th Year: {section_a}')"
pause
