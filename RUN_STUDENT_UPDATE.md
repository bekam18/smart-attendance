# 🚀 Run Student Update - Simple Instructions

## You're Already in Virtual Environment!

I can see `(venv)` in your prompt, so just run:

```powershell
python backend/update_real_students.py
```

Or if you're in the backend folder:

```powershell
python update_real_students.py
```

---

## After Update, Verify:

```powershell
python backend/verify_students.py
```

---

## Expected Result:

```
✅ 19 real students added
✅ Section A: 6 students
✅ Section B: 7 students  
✅ Section C: 6 students
```

---

## Quick Commands:

### From root directory:
```powershell
# Update students
python backend/update_real_students.py

# Verify
python backend/verify_students.py
```

### From backend directory:
```powershell
# Update students
python update_real_students.py

# Verify
python verify_students.py
```

---

## If You Get Import Error:

Make sure you're in the virtual environment:

```powershell
# Activate venv (if not already active)
.\venv\Scripts\Activate.ps1

# Then run update
python backend/update_real_students.py
```

---

## Test Login After Update:

Try logging in as:
- Username: `STU001`
- Password: `Nabila123`

---

**Just run: `python backend/update_real_students.py`** 🚀
