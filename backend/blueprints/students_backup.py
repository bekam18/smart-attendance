from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import os
import uuid

from db.mysql import get_db
from utils.security import role_required
from config import config

students_bp = Blueprint('students', __name__)

@students_bp.route('/profile', methods=['GET'])
@jwt_required()
@role_required('student')
def get_profile():
    """Get student profile with courses and instructors"""
    import json
    user_id = get_jwt_identity()
    db = get_db()
    
    student_result = db.execute_query('SELECT * FROM students WHERE user_id = %s', (user_id,))
    student = student_result[0] if student_result else None
    
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    # Get courses and instructors for this student
    instructor_query = "SELECT DISTINCT u.id, u.name, u.course_name, u.sections, u.class_year FROM users u WHERE u.role = 'instructor' AND u.class_year = %s"$')$')
    '''
    
    import json
    instructors_result = db.execute_query(instructor_query, (student.get('year', ''),))
    
    courses = []
    instructors = []
    student_section = student.get('section', 'A')
    
    if instructors_result:
        for instructor in instructors_result:
            # Check if instructor teaches this student's section
            sections_json = instructor.get('sections', '[]')
            try:
                sections = json.loads(sections_json) if isinstance(sections_json, str) else sections_json
                if student_section in sections:
                    courses.append(instructor.get('course_name', 'N/A'))
                    instructors.append({
                        'id': instructor['id'],
                        'name': instructor['name'],
                        'course': instructor.get('course_name', 'N/A')
                    })
            except:
                pass
    
    profile = {
        'id': str(student.get('id', student.get('_id', ''))),
        'student_id': student['student_id'],
        'name': student['name'],
        'email': student['email'],
        'department': student.get('department', ''),
        'year': student.get('year', ''),
        'section': student.get('section', ''),
        'face_registered': student.get('face_registered', False),
        'courses': list(set(courses)),  # Remove duplicates
        'instructors': instructors
    }
    
    return jsonify(profile), 200

@students_bp.route('/register-face', methods=['POST'])
@jwt_required()
@role_required('student')
def register_face():
    """Register face images for a student"""
    user_id = get_jwt_identity()
    db = get_db()
    
    student_result = db.execute_query('SELECT * FROM students WHERE user_id = %s', (user_id,))
    student = student_result[0] if student_result else None
    
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    # Check if files are provided
    if 'images' not in request.files:
        return jsonify({'error': 'No images provided'}), 400
    
    files = request.files.getlist('images')
    
    if len(files) == 0:
        return jsonify({'error': 'No images provided'}), 400
    
    # Create student folder
    student_folder = os.path.join(config.UPLOAD_FOLDER, 'faces', student['student_id'])
    os.makedirs(student_folder, exist_ok=True)
    
    saved_files = []
    for file in files:
        if file.filename:
            # Generate unique filename
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4()}.{ext}"
            filepath = os.path.join(student_folder, filename)
            
            file.save(filepath)
            saved_files.append(filename)
    
    # Update student record
    update_query = '''
        UPDATE students 
        SET face_registered = %s, face_images_count = %s, last_face_update = %s
        WHERE student_id = %s
    '''
    db.execute_query(update_query, (True, len(saved_files), datetime.utcnow(), student['student_id']), fetch=False)
    
    return jsonify({
        'message': 'Face images registered successfully',
        'images_count': len(saved_files)
    }), 200

@students_bp.route('/attendance', methods=['GET'])
@jwt_required()
@role_required('student')
def get_attendance():
    """Get student's attendance history"""
    user_id = get_jwt_identity()
    db = get_db()
    
    student_result = db.execute_query('SELECT * FROM students WHERE user_id = %s', (user_id,))
    student = student_result[0] if student_result else None
    
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    # Get attendance records
    attendance_records = db.execute_query('SELECT * FROM attendance WHERE student_id = %s ORDER BY timestamp DESC', (student['student_id'],))
    
    records = []
    for record in attendance_records:
        # Get session info
        session_result = db.execute_query('SELECT * FROM sessions WHERE id = %s', (record.get('session_id'),)) if record.get('session_id') else []
        session = session_result[0] if session_result else None
        
        records.append({
            'id': str(record.get('id', record.get('_id', ''))),
            'date': record['date'],
            'timestamp': record['timestamp'].isoformat(),
            'session_name': session.get('name', 'N/A') if session else 'N/A',
            'session_type': record.get('session_type', 'lab'),
            'course_name': record.get('course_name', 'N/A'),
            'confidence': record.get('confidence', 0),
            'status': record.get('status', 'present')
        })
    
    return jsonify(records), 200

@students_bp.route('/attendance/stats', methods=['GET'])
@jwt_required()
@role_required('student')
def get_attendance_stats():
    """Get student's attendance statistics with lab/theory breakdown"""
    user_id = get_jwt_identity()
    db = get_db()
    
    student_result = db.execute_query('SELECT * FROM students WHERE user_id = %s', (user_id,))
    student = student_result[0] if student_result else None
    
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    student_id = student['student_id']
    
    # Get all sessions for this student's year and section
    sessions_query = '''
        SELECT s.id, s.session_type, s.course_name
        FROM sessions s
        WHERE s.year = %s AND s.section_id = %s
    '''
    sessions = db.execute_query(sessions_query, (student.get('year', ''), student.get('section', '')))
    
    # Count total sessions by type
    total_lab_sessions = len([s for s in sessions if s.get('session_type') == 'lab'])
    total_theory_sessions = len([s for s in sessions if s.get('session_type') == 'theory'])
    
    # Get attendance records
    attendance_query = '''
        SELECT session_type, status, COUNT(*) as count
        FROM attendance
        WHERE student_id = %s
        GROUP BY session_type, status
    '''
    attendance_stats = db.execute_query(attendance_query, (student_id,))
    
    # Calculate statistics
    lab_present = 0
    lab_absent = 0
    theory_present = 0
    theory_absent = 0
    
    for stat in attendance_stats:
        session_type = stat.get('session_type', 'lab')
        status = stat.get('status', 'present')
        count = stat.get('count', 0)
        
        if session_type == 'lab':
            if status == 'present':
                lab_present = count
            else:
                lab_absent = count
        else:  # theory
            if status == 'present':
                theory_present = count
            else:
                theory_absent = count
    
    # Calculate percentages
    lab_total = lab_present + lab_absent
    theory_total = theory_present + theory_absent
    
    lab_percentage = (lab_present / lab_total * 100) if lab_total > 0 else 0
    theory_percentage = (theory_present / theory_total * 100) if theory_total > 0 else 0
    
    # Check warnings
    lab_warning = lab_percentage < 100
    theory_warning = theory_percentage < 80
    
    stats = {
        'lab': {
            'present': lab_present,
            'absent': lab_absent,
            'total': lab_total,
            'total_sessions': total_lab_sessions,
            'percentage': round(lab_percentage, 2),
            'required': 100,
            'warning': lab_warning
        },
        'theory': {
            'present': theory_present,
            'absent': theory_absent,
            'total': theory_total,
            'total_sessions': total_theory_sessions,
            'percentage': round(theory_percentage, 2),
            'required': 80,
            'warning': theory_warning
        },
        'overall': {
            'present': lab_present + theory_present,
            'absent': lab_absent + theory_absent,
            'total': lab_total + theory_total,
            'percentage': round(((lab_present + theory_present) / (lab_total + theory_total) * 100) if (lab_total + theory_total) > 0 else 0, 2)
        }
    }
    
    return jsonify(stats), 200
