import sys
sys.path.append('backend')
from db.mysql import get_db

db = get_db()

print("\n" + "="*60)
print("FINAL REPORT TEST - MOBILE DEVELOPMENT")
print("="*60)

# Use EXACT parameters
user_id = 58  # bacha
section_id = 'A'
course_name = 'Mobile Development'
start_date = '2025-12-01'
end_date = '2025-12-31'

print(f"\nParameters:")
print(f"  instructor_id: {user_id}")
print(f"  course_name: '{course_name}'")
print(f"  section_id: '{section_id}'")
print(f"  date_range: {start_date} to {end_date}")

# Build query (EXACT COPY FROM ENDPOINT)
sql = 'SELECT * FROM attendance WHERE 1=1'
params = []

sql += ' AND instructor_id = %s'
params.append(user_id)

if section_id:
    sql += ' AND section_id = %s'
    params.append(section_id)

if course_name:
    sql += ' AND course_name = %s'
    params.append(course_name)

if start_date:
    sql += ' AND date >= %s'
    params.append(start_date)

if end_date:
    sql += ' AND date <= %s'
    params.append(end_date)

sql += ' ORDER BY date, timestamp'

# Get records
records = db.execute_query(sql, tuple(params))
print(f"\n✅ Found {len(records)} attendance records")

# Get students
student_sql = 'SELECT * FROM students WHERE section = %s'
students = db.execute_query(student_sql, (section_id,))
print(f"✅ Found {len(students)} students in section")

# Process records (EXACT LOGIC FROM ENDPOINT)
student_stats = {}
session_ids = set()
session_types = {}

# First pass: collect sessions
for record in records:
    session_id = record.get('session_id')
    if session_id:
        session_ids.add(session_id)
        session_types[session_id] = record.get('session_type', 'theory')

print(f"\n📊 Unique sessions: {len(session_ids)} - IDs: {sorted(session_ids)}")

# Second pass: count attendance
for record in records:
    student_id = record['student_id']
    session_id = record.get('session_id')
    session_type = record.get('session_type', 'theory')
    status = record.get('status')
    
    if student_id not in student_stats:
        student_stats[student_id] = {
            'student_id': student_id,
            'name': '',
            'section': record.get('section_id', ''),
            'sessions_attended': set(),
            'lab_sessions_attended': set(),
            'theory_sessions_attended': set(),
            'total_sessions': 0,
            'present_count': 0,
            'absent_count': 0,
            'lab_sessions': 0,
            'lab_present': 0,
            'theory_sessions': 0,
            'theory_present': 0,
            'percentage': 0,
            'lab_percentage': 0,
            'theory_percentage': 0,
            'below_threshold': False
        }
    
    if session_id:
        student_stats[student_id]['sessions_attended'].add(session_id)
        
        if status == 'present':
            student_stats[student_id]['present_count'] += 1
            if session_type == 'lab':
                student_stats[student_id]['lab_sessions_attended'].add(session_id)
                student_stats[student_id]['lab_present'] += 1
            else:
                student_stats[student_id]['theory_sessions_attended'].add(session_id)
                student_stats[student_id]['theory_present'] += 1

# Count session types
total_lab_sessions = sum(1 for sid, stype in session_types.items() if stype == 'lab')
total_theory_sessions = sum(1 for sid, stype in session_types.items() if stype == 'theory')

print(f"   Lab sessions: {total_lab_sessions}")
print(f"   Theory sessions: {total_theory_sessions}")

# Add student names and calculate
for student in students:
    student_id = student['student_id']
    if student_id in student_stats:
        student_stats[student_id]['name'] = student['name']
        student_stats[student_id]['lab_sessions'] = total_lab_sessions
        student_stats[student_id]['theory_sessions'] = total_theory_sessions
        student_stats[student_id]['total_sessions'] = len(session_ids)
        student_stats[student_id]['absent_count'] = (
            student_stats[student_id]['total_sessions'] - 
            student_stats[student_id]['present_count']
        )
    else:
        # Student with no records
        student_stats[student_id] = {
            'student_id': student_id,
            'name': student['name'],
            'section': student.get('section', ''),
            'total_sessions': len(session_ids),
            'present_count': 0,
            'absent_count': len(session_ids),
            'lab_sessions': total_lab_sessions,
            'lab_present': 0,
            'theory_sessions': total_theory_sessions,
            'theory_present': 0,
            'percentage': 0,
            'lab_percentage': 0,
            'theory_percentage': 0,
            'below_threshold': True
        }

# Calculate percentages
for student_id, stats in student_stats.items():
    stats.pop('sessions_attended', None)
    stats.pop('lab_sessions_attended', None)
    stats.pop('theory_sessions_attended', None)
    
    if stats['total_sessions'] > 0:
        stats['percentage'] = (stats['present_count'] / stats['total_sessions']) * 100

# Print results
print("\n" + "="*60)
print("FINAL REPORT RESULTS:")
print("="*60)
print(f"Total Sessions: {len(session_ids)}")
print(f"Total Students: {len(student_stats)}")

print("\n📋 Student Details:")
for student_id in sorted(student_stats.keys()):
    stats = student_stats[student_id]
    print(f"\n  {student_id} - {stats['name']}")
    print(f"    Present: {stats['present_count']}")
    print(f"    Absent: {stats['absent_count']}")
    print(f"    Percentage: {stats['percentage']:.1f}%")

print("\n" + "="*60)
print("EXPECTED IN UI:")
print("="*60)
print("Total Sessions: 2")
print("STU013 (Bekam Ayele): 2 present, 0 absent, 100%")
print("All others: 0 present, 2 absent, 0%")
print("="*60 + "\n")
