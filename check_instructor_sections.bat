@echo off
echo Checking instructor sections in database...
echo.

python -c "import sys; sys.path.append('backend'); from db.mysql import get_db; import json; db = get_db(); result = db.execute_query('SELECT name, sections FROM users WHERE role=\"instructor\"'); [print(f'\nInstructor: {r[\"name\"]}\nSections: {json.loads(r[\"sections\"]) if r[\"sections\"] else \"None\"}') for r in result]"

pause
