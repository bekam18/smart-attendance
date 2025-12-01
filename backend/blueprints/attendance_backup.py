from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime, date
import logging
import traceback
import sys

from db.mongo import get_db
from utils.security import role_required
from recognizer.classifier import face_recognizer

attendance_bp = Blueprint('attendance', __name__)
logger = logging.getLogger(__name__)

# Add a before_request handler to log all requests
@attendance_bp.before_request
def log_request():
    logger.info(f"=== REQUEST: {request.method} {request.path} ===")
    print(f"\n{'='*60}")
    print(f"REQUEST: {request.method} {request.path}")
    print(f"{'='*60}")

@attendance_bp.route('/start-session', methods=['POST'])
@jwt_required()
@role_required('instructor')
def start_session():
    """Start a new attendance session"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    db = get_db()
    
    # Get instructor info
    instructor = db.users.find_one({'_id': ObjectId(user_id)})
    
    session_doc = {
        'instructor_id': user_id,
        'instructor_name': instructor.get('name', 'Unknown'),
        'name': data.get('name', f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"),
        'course': data.get('course', ''),
        'start_time': datetime.utcnow(),
        'end_time': None,
        'status': 'active',
        'attendance_count': 0
    }
    
    result = db.sessions.insert_one(session_doc)
    
    return jsonify({
        'message': 'Session started successfully',
        'session_id': str(result.inserted_id),
        'session': {
            'id': str(result.inserted_id),
            'name': session_doc['name'],
            'start_time': session_doc['start_time'].isoformat()
        }
    }), 201

@attendance_bp.route('/end-session', methods=['POST'])
@jwt_required()
@role_required('instructor')
def end_session():
    """End an attendance session"""
    data = request.get_json()
    
    if 'session_id' not in data:
        return jsonify({'error': 'Session ID required'}), 400
    
    db = get_db()
    
    # Update session
    result = db.sessions.update_one(
        {'_id': ObjectId(data['session_id'])},
        {
            '$set': {
                'end_time': datetime.utcnow(),
                'status': 'completed'
            }
        }
    )
    
    if result.matched_count == 0:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify({'message': 'Session ended successfully'}), 200

@attendance_bp.route('/recognize', methods=['POST'])
@jwt_required()
@role_required('instructor')
def recognize_face():
    """Recognize face and record attendance"""
    print("\n" + "="*60)
    print("RECOGNIZE ENDPOINT CALLED")
    print("="*60)
    sys.stdout.flush()
    
    try:
        print("🔍 Recognition request received")
        sys.stdout.flush()
        
        # Check if image is provided
        if 'image' not in request.files and 'image' not in request.form:
            print("❌ No image provided")
            return jsonify({'error': 'No image provided'}), 400
        
        # Get session_id
        session_id = request.form.get('session_id')
        if not session_id:
            print("❌ No session ID provided")
            return jsonify({'error': 'Session ID required'}), 400
        
        print(f"✅ Session ID: {session_id}")
        
        db = get_db()
        
        # Verify session exists and is active
        try:
            session = db.sessions.find_one({'_id': ObjectId(session_id)})
        except Exception as e:
            print(f"❌ Invalid session ID format: {e}")
            return jsonify({'error': 'Invalid session ID'}), 400
        
        if not session:
            print(f"❌ Session not found: {session_id}")
            return jsonify({'error': 'Session not found'}), 404
        
        if session['status'] != 'active':
            print(f"❌ Session not active: {session['status']}")
            return jsonify({'error': 'Session is not active'}), 400
        
        print("✅ Session verified")
        
        # Get image data
        try:
            if 'image' in request.files:
                image_file = request.files['image']
                image_data = image_file.read()
                print(f"✅ Image received from file: {len(image_data)} bytes")
            else:
                # Base64 image
                image_data = request.form.get('image')
                print(f"✅ Image received from form data")
        except Exception as e:
            print(f"❌ Error reading image: {e}")
            return jsonify({'error': f'Error reading image: {str(e)}'}), 400
        
        # Recognize face
        print("🔍 Starting face recognition...")
        try:
            result = face_recognizer.recognize(image_data)
            print(f"✅ Recognition result: {result['status']}")
        except Exception as e:
            print(f"❌ Recognition error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'status': 'error',
                'error': f'Recognition failed: {str(e)}',
                'message': 'Face recognition system encountered an error'
            }), 500
        
        if result['status'] == 'error':
            print(f"❌ Recognition returned error: {result.get('error')}")
            return jsonify(result), 500
        
        if result['status'] == 'no_face':
            print("⚠️ No face detected")
            return jsonify(result), 200
        
        if result['status'] == 'unknown':
            print("⚠️ Unknown face")
            return jsonify(result), 200
        
        if result['status'] == 'recognized':
            student_id = result['student_id']
            confidence = result['confidence']
            
            print(f"✅ Recognized: {student_id} (confidence: {confidence})")
            
            # Get student info
            student = db.students.find_one({'student_id': student_id})
            
            if not student:
                print(f"❌ Student not found in database: {student_id}")
                return jsonify({
                    'status': 'unknown',
                    'message': f'Student {student_id} not found in database'
                }), 200
            
            # Check if already marked present in this session
            today = date.today().isoformat()
            existing = db.attendance.find_one({
                'student_id': student_id,
                'session_id': session_id,
                'date': today
            })
            
            if existing:
                print(f"⚠️ Already marked: {student['name']}")
                return jsonify({
                    'status': 'already_marked',
                    'message': f'{student["name"]} already marked present in this session',
                    'student_id': student_id,
                    'student_name': student['name']
                }), 200
            
            # Record attendance
            attendance_doc = {
                'student_id': student_id,
                'session_id': session_id,
                'timestamp': datetime.utcnow(),
                'date': today,
                'confidence': confidence,
                'status': 'present'
            }
            
            db.attendance.insert_one(attendance_doc)
            
            # Update session attendance count
            db.sessions.update_one(
                {'_id': ObjectId(session_id)},
                {'$inc': {'attendance_count': 1}}
            )
            
            print(f"✅ Attendance recorded: {student['name']}")
            
            return jsonify({
                'status': 'recognized',
                'student_id': student_id,
                'student_name': student['name'],
                'confidence': confidence,
                'message': f'Attendance recorded for {student["name"]}'
            }), 200
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ EXCEPTION IN RECOGNIZE_FACE")
        print(f"{'='*60}")
        print(f"Error: {e}")
        print(f"Type: {type(e).__name__}")
        traceback.print_exc()
        sys.stdout.flush()
        
        return jsonify({
            'status': 'error',
            'error': str(e),
            'message': 'An unexpected error occurred',
            'type': type(e).__name__
        }), 500

@attendance_bp.route('/session/<session_id>', methods=['GET'])
@jwt_required()
@role_required('instructor', 'admin')
def get_session_attendance(session_id):
    """Get attendance for a specific session"""
    db = get_db()
    
    session = db.sessions.find_one({'_id': ObjectId(session_id)})
    
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    # Get attendance records
    attendance_records = db.attendance.find({'session_id': session_id})
    
    records = []
    for record in attendance_records:
        student = db.students.find_one({'student_id': record['student_id']})
        
        records.append({
            'student_id': record['student_id'],
            'student_name': student['name'] if student else 'Unknown',
            'timestamp': record['timestamp'].isoformat(),
            'confidence': record.get('confidence', 0)
        })
    
    return jsonify({
        'session': {
            'id': str(session['_id']),
            'name': session['name'],
            'start_time': session['start_time'].isoformat(),
            'status': session['status'],
            'attendance_count': session.get('attendance_count', 0)
        },
        'attendance': records
    }), 200

@attendance_bp.route('/student/<student_id>', methods=['GET'])
@jwt_required()
def get_student_attendance(student_id):
    """Get attendance records for a specific student"""
    db = get_db()
    
    student = db.students.find_one({'student_id': student_id})
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Get attendance records
    attendance_records = db.attendance.find(
        {'student_id': student_id}
    ).sort('timestamp', -1)
    
    records = []
    for record in attendance_records:
        session = db.sessions.find_one({'_id': ObjectId(record.get('session_id', ''))}) if record.get('session_id') else None
        
        records.append({
            'id': str(record['_id']),
            'date': record['date'],
            'timestamp': record['timestamp'].isoformat(),
            'session_name': session.get('name', 'N/A') if session else 'N/A',
            'confidence': record.get('confidence', 0)
        })
    
    return jsonify({
        'student': {
            'student_id': student['student_id'],
            'name': student['name']
        },
        'attendance': records
    }), 200

@attendance_bp.route('/test-recognition', methods=['POST'])
@jwt_required()
def test_recognition():
    """Test recognition without recording attendance - for debugging"""
    try:
        print("\n" + "="*60)
        print("TEST RECOGNITION REQUEST")
        print("="*60)
        
        # Check if image is provided
        if 'image' not in request.files and 'image' not in request.form:
            return jsonify({'error': 'No image provided'}), 400
        
        # Get image data
        try:
            if 'image' in request.files:
                image_file = request.files['image']
                image_data = image_file.read()
                print(f"Image from file: {len(image_data)} bytes")
            else:
                image_data = request.form.get('image')
                print(f"Image from form data")
        except Exception as e:
            print(f"Error reading image: {e}")
            return jsonify({'error': f'Error reading image: {str(e)}'}), 400
        
        # Test recognition
        print("Starting recognition test...")
        result = face_recognizer.recognize(image_data)
        print(f"Result: {result}")
        print("="*60 + "\n")
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Test recognition error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e),
            'type': type(e).__name__
        }), 500

@attendance_bp.route('/sessions', methods=['GET'])
@jwt_required()
@role_required('instructor', 'admin')
def get_sessions():
    """Get all sessions"""
    user_id = get_jwt_identity()
    db = get_db()
    
    # Get user role
    user = db.users.find_one({'_id': ObjectId(user_id)})
    
    # If instructor, only show their sessions
    query = {}
    if user['role'] == 'instructor':
        query['instructor_id'] = user_id
    
    sessions = db.sessions.find(query).sort('start_time', -1)
    
    session_list = []
    for session in sessions:
        session_list.append({
            'id': str(session['_id']),
            'name': session['name'],
            'instructor_name': session.get('instructor_name', 'Unknown'),
            'course': session.get('course', ''),
            'start_time': session['start_time'].isoformat(),
            'end_time': session['end_time'].isoformat() if session.get('end_time') else None,
            'status': session['status'],
            'attendance_count': session.get('attendance_count', 0)
        })
    
    return jsonify(session_list), 200
