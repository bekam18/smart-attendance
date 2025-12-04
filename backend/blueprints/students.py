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
    """Get student profile"""
    user_id = get_jwt_identity()
    db = get_db()
    
    student_result = db.execute_query('SELECT * FROM students WHERE user_id = %s', (user_id,))
    student = student_result[0] if student_result else None
    
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    profile = {
        'id': str(student['_id']),
        'student_id': student['student_id'],
        'name': student['name'],
        'email': student['email'],
        'department': student.get('department', ''),
        'year': student.get('year', ''),
        'face_registered': student.get('face_registered', False)
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
    db.students.update_one(
        {'_id': student['_id']},
        {
            '$set': {
                'face_registered': True,
                'face_images_count': len(saved_files),
                'last_face_update': datetime.utcnow()
            }
        }
    )
    
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
            'id': str(record['_id']),
            'date': record['date'],
            'timestamp': record['timestamp'].isoformat(),
            'session_name': session.get('name', 'N/A') if session else 'N/A',
            'confidence': record.get('confidence', 0),
            'status': record.get('status', 'present')
        })
    
    return jsonify(records), 200
