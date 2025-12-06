from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
import os

from db.mysql import get_db
from utils.security import hash_password, role_required
from config import config

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/add-instructor', methods=['POST'])
@jwt_required()
@role_required('admin')
def add_instructor():
    """Add a new instructor (admin only) - supports multiple courses"""
    data = request.get_json()
    
    # Support both old format (course_name) and new format (courses array)
    courses = data.get('courses', [])
    if not courses and data.get('course_name'):
        # Backward compatibility: convert single course to array
        courses = [data['course_name']]
    
    required_fields = ['username', 'password', 'email', 'name', 'class_year']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate at least one course
    if not courses or len(courses) == 0:
        return jsonify({'error': 'At least one course is required'}), 400
    
    # Validate session types - at least one must be selected
    lab_session = data.get('lab_session', False)
    theory_session = data.get('theory_session', False)
    
    if not lab_session and not theory_session:
        return jsonify({'error': 'At least one session type (Lab or Theory) must be selected'}), 400
    
    db = get_db()
    
    # Check if username or email already exists
    existing_user = db.execute_query("SELECT id FROM users WHERE username = %s OR email = %s", 
                                   (data['username'], data['email']))
    if existing_user:
        return jsonify({'error': 'Username or email already exists'}), 409
    
    # Build session types array
    session_types = []
    if lab_session:
        session_types.append('lab')
    if theory_session:
        session_types.append('theory')
    
    # Create instructor user with courses array
    import json
    query = """
        INSERT INTO users (username, password, email, name, role, department, course_name, courses, class_year, session_types, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    # Store first course in course_name for backward compatibility
    first_course = courses[0] if courses else ''
    
    values = (
        data['username'],
        hash_password(data['password']),
        data['email'],
        data['name'],
        'instructor',
        data.get('department', ''),
        first_course,  # Backward compatibility
        json.dumps(courses),  # New multi-course field
        str(data['class_year']),
        json.dumps(session_types),
        datetime.utcnow()
    )
    
    instructor_id = db.execute_query(query, values, fetch=False)
    
    print(f"✅ Instructor added: {data['name']} - Courses: {courses} - Year: {data['class_year']} - Sessions: {session_types}")
    
    return jsonify({
        'message': 'Instructor added successfully',
        'instructor_id': str(instructor_id)
    }), 201

@admin_bp.route('/instructors', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_instructors():
    """Get all instructors (admin only) - returns courses array"""
    import json
    db = get_db()
    
    instructors = db.execute_query("SELECT * FROM users WHERE role = 'instructor'")
    
    instructor_list = []
    for instructor in instructors:
        # Handle JSON session_types
        session_types = []
        if instructor.get('session_types'):
            try:
                session_types = json.loads(instructor['session_types'])
            except (json.JSONDecodeError, TypeError):
                # Fallback for comma-separated strings
                session_types = instructor['session_types'].split(',') if isinstance(instructor['session_types'], str) else []
        
        # Handle courses array (new format) or course_name (old format)
        courses = []
        if instructor.get('courses'):
            try:
                courses = json.loads(instructor['courses'])
            except (json.JSONDecodeError, TypeError):
                courses = []
        
        # Backward compatibility: if no courses array, use course_name
        if not courses and instructor.get('course_name'):
            courses = [instructor['course_name']]
        
        instructor_list.append({
            'id': str(instructor['id']),
            'username': instructor['username'],
            'name': instructor['name'],
            'email': instructor['email'],
            'department': instructor.get('department', ''),
            'course_name': instructor.get('course_name', ''),  # Keep for backward compatibility
            'courses': courses,  # New multi-course field
            'class_year': instructor.get('class_year', ''),
            'session_types': session_types,
            'enabled': instructor.get('enabled', True),
            'created_at': instructor['created_at'].isoformat() if instructor.get('created_at') else ''
        })
    
    return jsonify(instructor_list), 200

@admin_bp.route('/add-student', methods=['POST'])
@jwt_required()
@role_required('admin')
def add_student():
    """Add a new student (admin only)"""
    data = request.get_json()
    
    print(f"🔍 Add student request: {data}")
    
    required_fields = ['username', 'password', 'email', 'name', 'student_id']
    if not all(field in data for field in required_fields):
        missing = [f for f in required_fields if f not in data]
        print(f"❌ Missing fields: {missing}")
        return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
    
    db = get_db()
    
    # Check if username or email already exists
    existing_user = db.execute_query("SELECT id FROM users WHERE username = %s OR email = %s", 
                                   (data['username'], data['email']))
    if existing_user:
        print(f"❌ Username or email already exists: {data['username']}, {data['email']}")
        return jsonify({'error': 'Username or email already exists'}), 409
    
    # Check if student ID already exists
    existing_student = db.execute_query("SELECT id FROM students WHERE student_id = %s", (data['student_id'],))
    if existing_student:
        print(f"❌ Student ID already exists: {data['student_id']}")
        return jsonify({'error': 'Student ID already exists'}), 409
    
    # Create user
    user_query = """
        INSERT INTO users (username, password, email, name, role, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    user_values = (
        data['username'],
        hash_password(data['password']),
        data['email'],
        data['name'],
        'student',
        datetime.utcnow()
    )
    
    user_id = db.execute_query(user_query, user_values, fetch=False)
    
    # Create student profile
    student_query = """
        INSERT INTO students (user_id, student_id, name, email, department, year, section, face_registered, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    student_values = (
        user_id,
        data['student_id'],
        data['name'],
        data['email'],
        data.get('department', ''),
        data.get('year', ''),
        data.get('section', ''),
        False,
        datetime.utcnow()
    )
    
    db.execute_query(student_query, student_values, fetch=False)
    
    print(f"✅ Student added successfully: {data['student_id']}")
    
    return jsonify({
        'message': 'Student added successfully',
        'student_id': data['student_id']
    }), 201

@admin_bp.route('/students', methods=['GET'])
@jwt_required()
@role_required('admin', 'instructor')
def get_students():
    """Get all students"""
    db = get_db()
    
    # Join students with users to get enabled status
    query = """
        SELECT s.*, u.enabled 
        FROM students s 
        LEFT JOIN users u ON s.user_id = u.id
    """
    students = db.execute_query(query)
    
    student_list = []
    for student in students:
        student_list.append({
            'id': str(student['id']),
            'student_id': student['student_id'],
            'name': student['name'],
            'email': student['email'],
            'department': student.get('department', ''),
            'year_level': student.get('year', ''),  # Use 'year' from database
            'year': student.get('year', ''),  # For compatibility
            'section': student.get('section', ''),
            'face_registered': bool(student.get('face_registered', False)),
            'enabled': bool(student.get('enabled', True)),
            'created_at': student['created_at'].isoformat() if student.get('created_at') else ''
        })
    
    return jsonify(student_list), 200

@admin_bp.route('/attendance/all', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_all_attendance():
    """Get all attendance records with advanced filters (admin only)"""
    db = get_db()
    
    # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    student_id = request.args.get('student_id')
    section = request.args.get('section')
    instructor_id = request.args.get('instructor_id')
    
    # Build WHERE clause
    where_conditions = []
    params = []
    
    if start_date:
        where_conditions.append("a.date >= %s")
        params.append(start_date)
    if end_date:
        where_conditions.append("a.date <= %s")
        params.append(end_date)
    if student_id:
        where_conditions.append("a.student_id = %s")
        params.append(student_id)
    if section:
        where_conditions.append("s.section = %s")
        params.append(section)
    if instructor_id:
        where_conditions.append("a.instructor_id = %s")
        params.append(instructor_id)
    
    where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
    
    print(f"📊 Admin fetching attendance with filters: {dict(zip(['start_date', 'end_date', 'student_id', 'section', 'instructor_id'], [start_date, end_date, student_id, section, instructor_id]))}")
    
    # Get attendance records with joins (including sessions and course info)
    query = f"""
        SELECT 
            a.*, 
            s.name as student_name, 
            s.section, 
            u.name as instructor_name,
            sess.name as session_name,
            sess.session_type,
            sess.time_block,
            sess.course_name,
            sess.course as course_code
        FROM attendance a
        LEFT JOIN students s ON a.student_id = s.student_id
        LEFT JOIN users u ON a.instructor_id = u.id
        LEFT JOIN sessions sess ON a.session_id = sess.id
        {where_clause}
        ORDER BY a.timestamp DESC
        LIMIT 1000
    """
    
    attendance_records = db.execute_query(query, params)
    
    records = []
    for record in attendance_records:
        # Build session display with course info
        session_display = record.get('session_name') or 'Unknown'
        course_name = record.get('course_name')
        if course_name and session_display != 'Unknown':
            session_display = f"{course_name} - {session_display}"
        
        records.append({
            'id': str(record['id']),
            'student_id': record['student_id'],
            'student_name': record.get('student_name', 'Unknown'),
            'section': record.get('section', 'N/A'),
            'instructor_name': record.get('instructor_name', 'Unknown'),
            'instructor_id': record.get('instructor_id', ''),
            'session_id': record.get('session_id', ''),
            'session_name': session_display,
            'session_type': record.get('session_type', ''),
            'time_block': record.get('time_block', ''),
            'course_name': course_name or 'N/A',
            'course_code': record.get('course_code', ''),
            'timestamp': record['timestamp'].isoformat() if record.get('timestamp') else '',
            'date': record['date'],
            'confidence': float(record.get('confidence', 0)),
            'status': record.get('status', 'present')
        })
    
    print(f"✅ Returning {len(records)} attendance records")
    return jsonify(records), 200


@admin_bp.route('/attendance/export/csv', methods=['GET'])
@jwt_required()
@role_required('admin')
def export_attendance_csv():
    """Export all attendance records to CSV (admin only)"""
    from flask import make_response
    import csv
    from io import StringIO
    
    try:
        db = get_db()
        
        # Get filters from query params
        course = request.args.get('course')
        section = request.args.get('section')
        year = request.args.get('year')
        date = request.args.get('date')
        
        print(f"📊 CSV Export requested - Filters: course={course}, section={section}, year={year}, date={date}")
        
        # Build query with correct column names
        query = """
            SELECT 
                a.id,
                a.student_id,
                s.name as student_name,
                a.course_name,
                a.section_id,
                a.class_year,
                a.session_id,
                a.status,
                a.confidence,
                a.timestamp,
                a.date,
                a.instructor_id
            FROM attendance a
            LEFT JOIN students s ON a.student_id = s.student_id
            WHERE 1=1
        """
        params = []
        
        if course:
            query += " AND a.course_name = %s"
            params.append(course)
        if section:
            query += " AND a.section_id = %s"
            params.append(section)
        if year:
            query += " AND a.class_year = %s"
            params.append(year)
        if date:
            query += " AND a.date = %s"
            params.append(date)
        
        query += " ORDER BY a.timestamp DESC"
        
        # Execute query and get all records
        records = db.execute_query(query, tuple(params) if params else None)
        print(f"📊 Found {len(records)} records to export")
        
        # Create CSV
        si = StringIO()
        writer = csv.writer(si)
        
        # Write header
        writer.writerow([
            'ID', 'Student ID', 'Student Name', 'Course', 'Section', 
            'Year', 'Session ID', 'Status', 'Confidence', 'Date', 'Timestamp', 'Instructor ID'
        ])
        
        # Write data
        for record in records:
            try:
                writer.writerow([
                    record.get('id', ''),
                    record.get('student_id', ''),
                    record.get('student_name') or 'Unknown',
                    record.get('course_name', ''),
                    record.get('section_id', ''),
                    record.get('class_year', ''),
                    record.get('session_id', ''),
                    record.get('status', ''),
                    f"{record.get('confidence', 0):.2f}" if record.get('confidence') is not None else 'N/A',
                    str(record.get('date', '')),
                    str(record.get('timestamp', '')),
                    record.get('instructor_id') or 'N/A'
                ])
            except Exception as row_error:
                print(f"⚠️  Error writing row: {row_error}")
                print(f"   Record: {record}")
                continue
        
        # Create response
        output = si.getvalue()
        si.close()
        
        print(f"✅ CSV generated successfully ({len(output)} bytes)")
        
        response = make_response(output)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=attendance_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        response.headers['Cache-Control'] = 'no-cache'
        
        return response
        
    except Exception as e:
        print(f"❌ Error exporting CSV: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to export CSV: {str(e)}'}), 500


@admin_bp.route('/attendance/export/excel', methods=['GET'])
@jwt_required()
@role_required('admin')
def export_attendance_excel():
    """Export all attendance records to Excel (admin only)"""
    from flask import make_response
    import pandas as pd
    from io import BytesIO
    
    try:
        db = get_db()
        
        # Get filters from query params
        course = request.args.get('course')
        section = request.args.get('section')
        year = request.args.get('year')
        date = request.args.get('date')
        
        print(f"📊 Excel Export requested - Filters: course={course}, section={section}, year={year}, date={date}")
        
        # Build query with correct column names
        query = """
            SELECT 
                a.id,
                a.student_id,
                s.name as student_name,
                a.course_name,
                a.section_id,
                a.class_year,
                a.session_id,
                a.status,
                a.confidence,
                a.timestamp,
                a.date,
                a.instructor_id
            FROM attendance a
            LEFT JOIN students s ON a.student_id = s.student_id
            WHERE 1=1
        """
        params = []
        
        if course:
            query += " AND a.course_name = %s"
            params.append(course)
        if section:
            query += " AND a.section_id = %s"
            params.append(section)
        if year:
            query += " AND a.class_year = %s"
            params.append(year)
        if date:
            query += " AND a.date = %s"
            params.append(date)
        
        query += " ORDER BY a.timestamp DESC"
        
        # Execute query and get all records
        records = db.execute_query(query, tuple(params) if params else None)
        print(f"📊 Found {len(records)} records to export")
        
        if not records:
            # Return empty Excel file with headers
            df = pd.DataFrame(columns=[
                'ID', 'Student ID', 'Student Name', 'Course', 'Section',
                'Year', 'Session ID', 'Status', 'Confidence', 'Date', 'Timestamp', 'Instructor ID'
            ])
        else:
            # Convert to DataFrame
            df = pd.DataFrame(records)
            
            # Rename columns for better readability
            df = df.rename(columns={
                'id': 'ID',
                'student_id': 'Student ID',
                'student_name': 'Student Name',
                'course_name': 'Course',
                'section_id': 'Section',
                'class_year': 'Year',
                'session_id': 'Session ID',
                'status': 'Status',
                'confidence': 'Confidence',
                'date': 'Date',
                'timestamp': 'Timestamp',
                'instructor_id': 'Instructor ID'
            })
            
            # Format confidence
            if 'Confidence' in df.columns:
                df['Confidence'] = df['Confidence'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else 'N/A')
            
            # Fill NaN values
            df = df.fillna('N/A')
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Attendance Records')
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Attendance Records']
            for idx, col in enumerate(df.columns):
                try:
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(col)
                    ) + 2
                    col_letter = chr(65 + idx) if idx < 26 else chr(65 + idx // 26 - 1) + chr(65 + idx % 26)
                    worksheet.column_dimensions[col_letter].width = min(max_length, 50)
                except:
                    pass
        
        output.seek(0)
        
        print(f"✅ Excel generated successfully ({output.getbuffer().nbytes} bytes)")
        
        # Create response
        response = make_response(output.read())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename=attendance_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        response.headers['Cache-Control'] = 'no-cache'
        
        return response
        
    except Exception as e:
        print(f"❌ Error exporting Excel: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to export Excel: {str(e)}'}), 500

@admin_bp.route('/upload-model', methods=['POST'])
@jwt_required()
@role_required('admin')
def upload_model():
    """Upload model files (admin only)"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    file_type = request.form.get('type', 'classifier')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save file to models directory
    filename_map = {
        'classifier': 'face_classifier_v1.pkl',
        'encoder': 'label_encoder.pkl',
        'classes': 'label_encoder_classes.npy'
    }
    
    filename = filename_map.get(file_type, file.filename)
    filepath = os.path.join(config.MODEL_PATH, filename)
    
    file.save(filepath)
    
    return jsonify({
        'message': 'Model file uploaded successfully',
        'filename': filename
    }), 200

@admin_bp.route('/instructor/<instructor_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_instructor(instructor_id):
    """Delete an instructor (admin only)"""
    db = get_db()
    
    try:
        result = db.execute_query("DELETE FROM users WHERE id = %s AND role = 'instructor'", 
                                (instructor_id,), fetch=False)
        
        if db.cursor.rowcount == 0:
            return jsonify({'error': 'Instructor not found'}), 404
        
        print(f"✅ Instructor deleted: {instructor_id}")
        return jsonify({'message': 'Instructor deleted successfully'}), 200
        
    except Exception as e:
        print(f"❌ Error deleting instructor: {e}")
        return jsonify({'error': 'Failed to delete instructor'}), 500

@admin_bp.route('/student/<student_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_student(student_id):
    """Delete a student (admin only)"""
    db = get_db()
    
    try:
        # Find student to get user_id and student_id
        student = db.execute_query("SELECT user_id, student_id FROM students WHERE id = %s", (student_id,))
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        student = student[0]
        
        # Delete attendance records first (foreign key constraint)
        db.execute_query("DELETE FROM attendance WHERE student_id = %s", (student['student_id'],), fetch=False)
        
        # Delete student record
        db.execute_query("DELETE FROM students WHERE id = %s", (student_id,), fetch=False)
        
        # Delete user record
        db.execute_query("DELETE FROM users WHERE id = %s", (student['user_id'],), fetch=False)
        
        print(f"✅ Student deleted: {student_id}")
        return jsonify({'message': 'Student deleted successfully'}), 200
        
    except Exception as e:
        print(f"❌ Error deleting student: {e}")
        return jsonify({'error': 'Failed to delete student'}), 500

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_stats():
    """Get system statistics with optional date filter (admin only)"""
    from datetime import datetime as dt, timedelta
    
    db = get_db()
    
    # Get date parameter (default to today)
    date_param = request.args.get('date')
    
    if date_param:
        # Use provided date
        target_date = date_param
    else:
        # Default to today
        target_date = dt.now().strftime('%Y-%m-%d')
    
    # Calculate 12 hours ago from the target date
    target_datetime = dt.strptime(target_date, '%Y-%m-%d')
    twelve_hours_ago = target_datetime - timedelta(hours=12)
    
    print(f"📊 Getting stats for date: {target_date}")
    
    # Base stats (always total)
    total_students = db.execute_query("SELECT COUNT(*) as count FROM students")[0]['count']
    total_instructors = db.execute_query("SELECT COUNT(*) as count FROM users WHERE role = 'instructor'")[0]['count']
    students_with_face = db.execute_query("SELECT COUNT(*) as count FROM students WHERE face_registered = 1")[0]['count']
    
    stats = {
        'total_students': total_students,
        'total_instructors': total_instructors,
        'students_with_face': students_with_face,
        'selected_date': target_date
    }
    
    # Date-filtered stats
    if date_param:
        # Specific date - show all records for that day
        attendance_count = db.execute_query("SELECT COUNT(*) as count FROM attendance WHERE date = %s", (target_date,))[0]['count']
        active_sessions = db.execute_query(
            "SELECT COUNT(*) as count FROM sessions WHERE status = 'active' AND DATE(start_time) = %s", 
            (target_date,)
        )[0]['count']
        stats['total_attendance_records'] = attendance_count
        stats['active_sessions'] = active_sessions
    else:
        # Today - show last 12 hours
        attendance_count = db.execute_query(
            "SELECT COUNT(*) as count FROM attendance WHERE date = %s AND timestamp >= %s", 
            (target_date, twelve_hours_ago)
        )[0]['count']
        active_sessions = db.execute_query("SELECT COUNT(*) as count FROM sessions WHERE status = 'active'")[0]['count']
        stats['total_attendance_records'] = attendance_count
        stats['active_sessions'] = active_sessions
    
    print(f"✅ Stats: {stats}")
    return jsonify(stats), 200


@admin_bp.route('/settings', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_admin_settings():
    """Get admin settings"""
    db = get_db()
    
    # Check if admin_settings table exists, if not create it
    try:
        settings = db.execute_query("SELECT * FROM admin_settings LIMIT 1")
    except:
        # Create table if it doesn't exist
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS admin_settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                face_recognition_threshold DECIMAL(3,2) DEFAULT 0.60,
                session_timeout_minutes INT DEFAULT 120,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """, fetch=False)
        settings = []
    
    if not settings:
        # Return defaults
        return jsonify({
            'face_recognition_threshold': 0.60,
            'session_timeout_minutes': 120
        }), 200
    
    settings = settings[0]
    return jsonify({
        'face_recognition_threshold': float(settings.get('face_recognition_threshold', 0.60)),
        'session_timeout_minutes': int(settings.get('session_timeout_minutes', 120))
    }), 200


@admin_bp.route('/settings', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_admin_settings():
    """Update admin settings"""
    try:
        data = request.get_json()
        db = get_db()
        
        face_threshold = float(data.get('face_recognition_threshold', 0.60))
        timeout_minutes = int(data.get('session_timeout_minutes', 120))
        
        # Check if settings exist
        existing = db.execute_query("SELECT id FROM admin_settings LIMIT 1")
        
        if existing:
            # Update existing
            db.execute_query("""
                UPDATE admin_settings 
                SET face_recognition_threshold = %s, session_timeout_minutes = %s, updated_at = %s
                WHERE id = %s
            """, (face_threshold, timeout_minutes, datetime.utcnow(), existing[0]['id']), fetch=False)
        else:
            # Insert new
            db.execute_query("""
                INSERT INTO admin_settings (face_recognition_threshold, session_timeout_minutes, updated_at)
                VALUES (%s, %s, %s)
            """, (face_threshold, timeout_minutes, datetime.utcnow()), fetch=False)
        
        print(f"✅ Admin settings updated: threshold={face_threshold}, timeout={timeout_minutes}")
        return jsonify({'message': 'Settings updated successfully'}), 200
    
    except Exception as e:
        print(f"❌ Error updating settings: {e}")
        return jsonify({'error': 'Failed to update settings', 'message': str(e)}), 500


# TODO: Fix sessions for MySQL
# @admin_bp.route('/active-sessions', methods=['GET'])
# @jwt_required()
# @role_required('admin')
# def get_active_sessions():
#     """Get currently active sessions with filters"""
#     return jsonify([]), 200  # Return empty array for now


# TODO: Fix sessions for MySQL
# @admin_bp.route('/recent-sessions', methods=['GET'])
# @jwt_required()
# @role_required('admin')
# def get_recent_sessions():
#     """Get recent completed sessions with filters"""
#     return jsonify([]), 200  # Return empty array for now


@admin_bp.route('/instructor/<instructor_id>/toggle', methods=['PUT'])
@jwt_required()
@role_required('admin')
def toggle_instructor(instructor_id):
    """Enable/Disable an instructor (admin only)"""
    try:
        db = get_db()
        
        instructor = db.execute_query("SELECT enabled FROM users WHERE id = %s AND role = 'instructor'", (instructor_id,))
        
        if not instructor:
            return jsonify({'error': 'Instructor not found'}), 404
        
        # Toggle enabled status
        current_status = bool(instructor[0].get('enabled', True))
        new_status = not current_status
        
        db.execute_query("UPDATE users SET enabled = %s WHERE id = %s", (new_status, instructor_id), fetch=False)
        
        status_text = 'enabled' if new_status else 'disabled'
        print(f"✅ Instructor {instructor_id} {status_text}")
        
        return jsonify({
            'message': f'Instructor {status_text} successfully',
            'enabled': new_status
        }), 200
        
    except Exception as e:
        print(f"❌ Error toggling instructor: {e}")
        return jsonify({'error': 'Failed to toggle instructor'}), 500


@admin_bp.route('/student/<student_id>/toggle', methods=['PUT'])
@jwt_required()
@role_required('admin')
def toggle_student(student_id):
    """Enable/Disable a student (admin only)"""
    try:
        db = get_db()
        
        # Get student and user info
        student_user = db.execute_query("""
            SELECT s.id, s.user_id, u.enabled 
            FROM students s 
            JOIN users u ON s.user_id = u.id 
            WHERE s.id = %s
        """, (student_id,))
        
        if not student_user:
            return jsonify({'error': 'Student not found'}), 404
        
        student_user = student_user[0]
        
        # Toggle enabled status
        current_status = bool(student_user.get('enabled', True))
        new_status = not current_status
        
        db.execute_query("UPDATE users SET enabled = %s WHERE id = %s", 
                        (new_status, student_user['user_id']), fetch=False)
        
        status_text = 'enabled' if new_status else 'disabled'
        print(f"✅ Student {student_id} {status_text}")
        
        return jsonify({
            'message': f'Student {status_text} successfully',
            'enabled': new_status
        }), 200
        
    except Exception as e:
        print(f"❌ Error toggling student: {e}")
        return jsonify({'error': 'Failed to toggle student'}), 500


@admin_bp.route('/instructor/<instructor_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_instructor(instructor_id):
    """Update instructor details (admin only) - supports multiple courses"""
    try:
        import json
        data = request.get_json()
        db = get_db()
        
        instructor = db.execute_query("SELECT id FROM users WHERE id = %s AND role = 'instructor'", (instructor_id,))
        
        if not instructor:
            return jsonify({'error': 'Instructor not found'}), 404
        
        # Build update fields
        update_fields = []
        update_values = []
        
        if 'name' in data:
            update_fields.append('name = %s')
            update_values.append(data['name'])
        if 'email' in data:
            update_fields.append('email = %s')
            update_values.append(data['email'])
        if 'department' in data:
            update_fields.append('department = %s')
            update_values.append(data['department'])
        if 'class_year' in data:
            update_fields.append('class_year = %s')
            update_values.append(str(data['class_year']))
        
        # Handle courses array (new format)
        if 'courses' in data:
            courses = data['courses']
            if not courses or len(courses) == 0:
                return jsonify({'error': 'At least one course is required'}), 400
            
            update_fields.append('courses = %s')
            update_values.append(json.dumps(courses))
            
            # Update course_name for backward compatibility
            update_fields.append('course_name = %s')
            update_values.append(courses[0] if courses else '')
        
        # Handle session types
        if 'lab_session' in data or 'theory_session' in data:
            session_types = []
            if data.get('lab_session', False):
                session_types.append('lab')
            if data.get('theory_session', False):
                session_types.append('theory')
            
            if not session_types:
                return jsonify({'error': 'At least one session type must be selected'}), 400
            
            update_fields.append('session_types = %s')
            update_values.append(json.dumps(session_types))
        
        if update_fields:
            update_values.append(instructor_id)
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
            db.execute_query(query, update_values, fetch=False)
        
        print(f"✅ Instructor {instructor_id} updated")
        return jsonify({'message': 'Instructor updated successfully'}), 200
        
    except Exception as e:
        print(f"❌ Error updating instructor: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to update instructor', 'message': str(e)}), 500


@admin_bp.route('/student/<student_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_student(student_id):
    """Update student details (admin only)"""
    try:
        data = request.get_json()
        db = get_db()
        
        student = db.execute_query("SELECT user_id FROM students WHERE id = %s", (student_id,))
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        user_id = student[0]['user_id']
        
        # Update student document
        student_fields = []
        student_values = []
        
        if 'name' in data:
            student_fields.append('name = %s')
            student_values.append(data['name'])
        if 'email' in data:
            student_fields.append('email = %s')
            student_values.append(data['email'])
        if 'department' in data:
            student_fields.append('department = %s')
            student_values.append(data['department'])
        if 'year' in data:
            student_fields.append('year = %s')
            student_values.append(data['year'])
        if 'section' in data:
            student_fields.append('section = %s')
            student_values.append(data['section'])
        
        if student_fields:
            student_values.append(student_id)
            query = f"UPDATE students SET {', '.join(student_fields)} WHERE id = %s"
            db.execute_query(query, student_values, fetch=False)
        
        # Update user document
        user_fields = []
        user_values = []
        
        if 'name' in data:
            user_fields.append('name = %s')
            user_values.append(data['name'])
        if 'email' in data:
            user_fields.append('email = %s')
            user_values.append(data['email'])
        
        if user_fields:
            user_values.append(user_id)
            query = f"UPDATE users SET {', '.join(user_fields)} WHERE id = %s"
            db.execute_query(query, user_values, fetch=False)
        
        print(f"✅ Student {student_id} updated")
        return jsonify({'message': 'Student updated successfully'}), 200
        
    except Exception as e:
        print(f"❌ Error updating student: {e}")
        return jsonify({'error': 'Failed to update student'}), 500
