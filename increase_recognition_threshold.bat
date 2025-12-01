@echo off
echo ========================================
echo Increase Face Recognition Threshold
echo ========================================
echo.
echo Current threshold: 0.60 (60%%)
echo This is TOO LOW and causes false positives
echo.
echo Recommended threshold: 0.75-0.80 (75-80%%)
echo This will reduce confusion between similar faces
echo.
echo ========================================
echo.

cd backend

python -c "
import re

# Read classifier.py
with open('recognizer/classifier.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace threshold values
content = re.sub(r'self\.threshold = 0\.60', 'self.threshold = 0.75', content)
content = re.sub(r'NEW_THRESHOLD = 0\.60', 'NEW_THRESHOLD = 0.75', content)

# Write back
with open('recognizer/classifier.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Threshold updated from 0.60 to 0.75')
print('✅ This will reject matches below 75%% confidence')
print('')
print('Example:')
print('  Before: Bedo (62.6%%) → ACCEPTED (wrong student)')
print('  After:  Bedo (62.6%%) → REJECTED (shown as unknown)')
print('')
print('⚠️  You must RESTART the backend server for changes to take effect!')
"

echo.
echo ========================================
echo Threshold Updated!
echo ========================================
echo.
echo IMPORTANT: Restart your backend server:
echo   1. Stop current backend (Ctrl+C)
echo   2. cd backend
echo   3. python app.py
echo.
echo Then test face recognition again.
echo.
pause
