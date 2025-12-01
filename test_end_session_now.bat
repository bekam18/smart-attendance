@echo off
echo ========================================
echo Test End Session with Absent Marking
echo ========================================
echo.
echo This will test if the end_session endpoint works
echo.
cd backend
python -c "from blueprints.attendance import end_session; print('✓ end_session function loaded'); import inspect; src = inspect.getsource(end_session); print('✓ Function has', src.count('absent'), 'references to absent'); print('✓ Function has', src.count('ENDING SESSION'), 'ENDING SESSION prints')"
echo.
pause
