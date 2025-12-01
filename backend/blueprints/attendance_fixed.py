"""
Fixed Attendance Blueprint with Comprehensive Error Handling
Handles base64 images, file uploads, and all error scenarios gracefully
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime, date
import logging
import traceback
import sys
import base64
import io
from PIL import Image
import numpy as np

from db.mongo import get_db
from utils.security import role_required

attendance_bp = Blueprint('attendance', __name__)
logger = logging.getLogger(__name__)


def decode_image_data(image_data):
    """
    Decode image from various formats: base64, file bytes, or data URL
    Returns: numpy array (BGR format for OpenCV)
    """
    try:
        # Case 1: String (base64 or data URL)
        if isinstance(image_data, str):
            # Remove data URL prefix if present
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
        
        # Case 2: Already bytes
        elif isinstance(image_data, bytes):
            image_bytes = image_data
        
        else:
            raise ValueError(f"Unsupported image data type: {type(image_data)}")
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array (RGB)
        img_array = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        import cv2
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        return img_bgr
        
    except Exception as e:
        logger.error(f"Image decoding error: {e}")
        raise ValueError(f"Failed to decode image: {str(e)}")


@attendance_bp.route('/recognize', methods=['POST', 'OPTIONS'])
@jwt_required()
@role_required('instructor')
def recognize_face():
    """
    Recognize face and record attendance
    
    Accepts:
    - multipart/form-data with 'image' file and 'session_id'
    - application/json with 'image' (base64) and 'session_id'
    
    Returns:
    - 200: Success with recognition result
    - 400: Bad request (missing data, invalid format)
    - 404: Session not found
    - 500: Server error
    """
    
    # Log request
    print("\n" + "="*80)
    print("RECOGNIZE FACE REQUEST")
    print("="*80)
    print(f"Method: {request.method}")
    print(f"Content-Type: {request.content_type}")
    print(f"Form keys: {list(request.form.keys())}")
    print(f"Files keys: {list(request.files.keys())}")
    sys.stdout.flush()
    
    try:
        # ============================================================
        # STEP 1: Extract and validate input data
        # ============================================================
        
        image_data = None
        session_id = None
        
        # Try to get image from different sources
        if request.files and 'image' in request.files:
            # Multipart form data with file
            image_file = request.files['image']
            image_data = image_file.read()
            print(f"✓ Image from file upload: {len(image_data)} bytes")
        
        elif request.form and 'image' in request.form:
            # Form data with base64 string
            image_data = request.form.get('image')
            print(f"✓ Image from form data (base64)")
        
        elif request.is_json and request.json:
            # JSON body
            json_data = request.json
            image_data = json_data.get('image')
            session_id = json_data.get('session_id')
            print(f"✓ Image from JSON body")
        
        else:
            print("✗ No image data found in request")
            return jsonify({
                'status': 'error',
                'error': 'No image provided',
                'message': 'Please provide an image in the request'
            }), 400
        
        # Get session_id if not already extracted
        if not session_id:
            session_id = request.form.get('session_id') or (request.json.get('session_id') if request.is_json else None)
        
        if not session_id:
            print("✗ No session_id provided")
            return jsonify({
                'status': 'error',
                'error': 'Session ID required',
                'message': 'Please provide a session_id'
            }), 400
        
        print(f"✓ Session ID: {session_id}")
        sys.stdout.flush()
        
        # ============================================================
        # STEP 2: Validate session
        # ============================================================
        
        db = get_db()
        
        try:
            session = db.sessions.find_one({'_id': ObjectId(session_id)})
        except Exception as e:
            print(f"✗ Invalid session ID format: {e}")
            return jsonify({
                'status': 'error',
                'error': 'Invalid session ID format',
                'message': str(e)
            }), 400
        
        if not session:
            print(f"✗ Session not found: {session_id}")
            return jsonify({
                'status': 'error',
                'error': 'Session not found',
                'message': f'Session {session_id} does not exist'
            }), 404
        
        if session.get('status') != 'active':
            print(f"✗ Session not active: {session.get('status')}")
            return jsonify({
                'status': 'error',
                'error': 'Session not active',
                'message': f'Session status is {session.get("status")}'
            }), 400
        
        print("✓ Session validated")
        sys.stdout.flush()
        
        # ============================================================
        # STEP 3: Decode image
        # ============================================================
        
        try:
            img_array = decode_image_data(image_data)
            print(f"✓ Image decoded: shape {img_array.shape}")
            sys.stdout.flush()
        except Exception as e:
            print(f"✗ Image decoding failed: {e}")
            traceback.print_exc()
            return jsonify({
                'status': 'error',
                'error': 'Image decoding failed',
                'message': str(e)
            }), 400
        
        # ============================================================
        # STEP 4: Perform face recognition
        # ============================================================
        
        try:
            from recognizer.classifier import face_recognizer
            
            print("→ Starting face recognition...")
            sys.stdout.flush()
            
            result = face_recognizer.recognize(img_array)
            
            print(f"✓ Recognition complete: {result.get('status')}")
            sys.stdout.flush()
            
        except ImportError as e:
            print(f"✗ Import error: {e}")
            traceback.print_exc()
            return jsonify({
                'status': 'error',
                'error': 'Recognition system not available',
                'message': 'Face recognition dependencies not loaded. Check server logs.'
            }), 500
        
        except Exception as e:
            print(f"✗ Recognition error: {e}")
            traceback.print_exc()
            return jsonify({
                'status': 'error',
                'error': 'Recognition failed',
                'message': str(e),
                'type': type(e).__name__
            }), 500
        
        # ============================================================
        # STEP 5: Handle recognition results
        # ============================================================
        
        # Error during recognition
        if result.get('status') == 'error':
            print(f"✗ Recognition returned error: {result.get('error')}")
            return jsonify(result), 200  # Return 200 with error status
        
        # No face detected
        if result.get('status') == 'no_face':
            print("⚠ No face detected")
            return jsonify(result), 200
        
        # Unknown face (low confidence)
        if result.get('status') == 'unknown':
            print("⚠ Unknown face (low confidence)")
            return jsonify(result), 200
        
        # Face recognized
        if result.get('status') == 'recognized':
            student_id = result.get('student_id')
            confidence = result.get('confidence', 0)
            
            print(f"✓ Recognized: {student_id} (confidence: {confidence:.4f})")
            
            # Get student info
            student = db.students.find_one({'student_id': student_id})
            
            if not student:
                print(f"✗ Student not in database: {student_id}")
                return jsonify({
                    'status': 'unknown',
                    'message': f'Student {student_id} not found in database'
                }), 200
            
            # Check if already marked present
            today = date.today().isoformat()
            existing = db.attendance.find_one({
                'student_id': student_id,
                'session_id': session_id,
                'date': today
            })
            
            if existing:
                print(f"⚠ Already marked: {student.get('name')}")
                return jsonify({
                    'status': 'already_marked',
                    'message': f'{student.get("name")} already marked present',
                    'student_id': student_id,
                    'student_name': student.get('name')
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
            
            # Update session count
            db.sessions.update_one(
                {'_id': ObjectId(session_id)},
                {'$inc': {'attendance_count': 1}}
            )
            
            print(f"✓ Attendance recorded: {student.get('name')}")
            print("="*80 + "\n")
            sys.stdout.flush()
            
            return jsonify({
                'status': 'recognized',
                'student_id': student_id,
                'student_name': student.get('name'),
                'confidence': confidence,
                'message': f'Attendance recorded for {student.get("name")}'
            }), 200
        
        # Unknown status
        print(f"⚠ Unknown recognition status: {result.get('status')}")
        return jsonify(result), 200
    
    except Exception as e:
        # Catch-all for any unexpected errors
        print("\n" + "="*80)
        print("UNEXPECTED ERROR IN RECOGNIZE_FACE")
        print("="*80)
        print(f"Error: {e}")
        print(f"Type: {type(e).__name__}")
        traceback.print_exc()
        print("="*80 + "\n")
        sys.stdout.flush()
        
        return jsonify({
            'status': 'error',
            'error': 'Unexpected server error',
            'message': str(e),
            'type': type(e).__name__
        }), 500


# Other endpoints remain the same...
@attendance_bp.route('/start-session', methods=['POST'])
@jwt_required()
@role_required('instructor')
def start_session():
    """Start a new attendance session"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        db = get_db()
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
    
    except Exception as e:
        logger.error(f"Error starting session: {e}", exc_info=True)
        return jsonify({
            'error': 'Failed to start session',
            'message': str(e)
        }), 500


@attendance_bp.route('/end-session', methods=['POST'])
@jwt_required()
@role_required('instructor')
def end_session():
    """End an attendance session"""
    try:
        data = request.get_json()
        
        if 'session_id' not in data:
            return jsonify({'error': 'Session ID required'}), 400
        
        db = get_db()
        
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
    
    except Exception as e:
        logger.error(f"Error ending session: {e}", exc_info=True)
        return jsonify({
            'error': 'Failed to end session',
            'message': str(e)
        }), 500


@attendance_bp.route('/sessions', methods=['GET'])
@jwt_required()
@role_required('instructor', 'admin')
def get_sessions():
    """Get all sessions"""
    try:
        user_id = get_jwt_identity()
        db = get_db()
        
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
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
    
    except Exception as e:
        logger.error(f"Error getting sessions: {e}", exc_info=True)
        return jsonify({
            'error': 'Failed to get sessions',
            'message': str(e)
        }), 500
