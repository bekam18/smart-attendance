"""
Fixed Attendance Blueprint with Comprehensive Error Handling
Handles base64 images, file uploads, and all error scenarios gracefully
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta
import logging
import traceback
import sys
import os
import base64
import io
from PIL import Image
import numpy as np

from db.mysql import get_db
from utils.security import role_required
from utils.timezone_helper import get_ethiopian_time, convert_utc_to_ethiopian, format_time_for_display
from middleware.working_security import working_security_check, working_audit_log

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


@attendance_bp.route('/test-ping', methods=['GET'])
def test_ping():
    """Test endpoint - no auth required"""
    print("TEST PING RECEIVED!")
    return jsonify({'status': 'ok', 'message': 'Attendance blueprint is working'}), 200


@attendance_bp.route('/detect-face', methods=['POST'])
@jwt_required()
def detect_face():
    """
    Detect face in image and return bounding box + landmarks
    Used for real-time face tracking overlay
    
    Returns:
    - 200: Success with face detection data
    - 400: Bad request
    - 500: Server error
    """
    try:
        # Extract image data
        image_data = None
        
        if request.files and 'image' in request.files:
            image_file = request.files['image']
            image_data = image_file.read()
        elif request.form and 'image' in request.form:
            image_data = request.form.get('image')
        elif request.is_json and request.json:
            image_data = request.json.get('image')
        else:
            return jsonify({
                'status': 'error',
                'error': 'No image provided'
            }), 400
        
        # Decode image
        try:
            img_array = decode_image_data(image_data)
        except Exception as e:
            return jsonify({
                'status': 'error',
                'error': 'Image decoding failed',
                'message': str(e)
            }), 400
        
        # Detect faces with improved detector
        try:
            print("🔍 Using Improved Face Detector...")
            from recognizer.detector_improved import get_face_detector
            
            detector = get_face_detector(method='insightface')
            print("✓ Improved detector loaded")
            
            print(f"🔍 Detecting faces in image shape: {img_array.shape}")
            
            # Detect faces with confidence scores
            results = detector.detect_faces(img_array, return_confidence=True)
            print(f"✓ Detection complete, found {len(results)} faces")
            
            if len(results) == 0:
                print("⚠️ No faces detected")
                return jsonify({
                    'status': 'no_face',
                    'faces': []
                }), 200
            
            # Convert face data to JSON-serializable format
            face_data = []
            for bbox, confidence in results:
                x, y, w, h = bbox
                print(f"✓ Face bbox: x={x}, y={y}, w={w}, h={h}, confidence={confidence:.2f}")
                
                face_data.append({
                    'bbox': {
                        'x': int(x),
                        'y': int(y),
                        'w': int(w),
                        'h': int(h)
                    },
                    'confidence': float(confidence),
                    'landmarks': []  # Can be added if needed
                })
            
            return jsonify({
                'status': 'success',
                'faces': face_data,
                'count': len(face_data)
            }), 200
            
        except Exception as e:
            logger.error(f"Face detection error: {e}")
            traceback.print_exc()
            return jsonify({
                'status': 'error',
                'error': 'Detection failed',
                'message': str(e)
            }), 500
    
    except Exception as e:
        logger.error(f"Unexpected error in detect_face: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': 'Unexpected server error',
            'message': str(e)
        }), 500


@attendance_bp.route('/recognize', methods=['POST'])
@working_security_check
@working_audit_log('FACE_RECOGNITION')
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
    
    # ============================================================
    # WORKING HOURS VALIDATION
    # ============================================================
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from utils.time_restrictions import is_within_working_hours
    
    time_check = is_within_working_hours()
    
    if not time_check['allowed']:
        print(f"🚫 BLOCKED: Outside working hours - {time_check['message']}")
        return jsonify({
            'status': 'time_blocked',
            'message': time_check['message'],
            'current_time': time_check['current_time'],
            'next_period': time_check['next_period'],
            'minutes_until_next': time_check.get('minutes_until_next', 0),
            'working_hours': {
                'morning': '8:30 AM - 12:30 PM',
                'afternoon': '1:30 PM - 5:30 PM',
                'lunch_break': '12:30 PM - 1:30 PM (blocked)'
            }
        }), 403
    
    print(f"✅ WORKING HOURS OK: {time_check['message']}")
    
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
            session_result = db.execute_query('SELECT * FROM sessions WHERE id = %s', (session_id,))
        except Exception as e:
            print(f"✗ Invalid session ID format: {e}")
            return jsonify({
                'status': 'error',
                'error': 'Invalid session ID format',
                'message': str(e)
            }), 400
        
        if not session_result:
            print(f"✗ Session not found: {session_id}")
            return jsonify({
                'status': 'error',
                'error': 'Session not found',
                'message': f'Session {session_id} does not exist'
            }), 404
        
        session = session_result[0]  # Get the first result
        
        if session.get('status') != 'active':
            print(f"✗ Session not active: {session.get('status')}")
            return jsonify({
                'status': 'error',
                'error': 'Session not active',
                'message': f'Session status is {session.get("status")}'
            }), 400
        
        print("✓ Session validated")
        
        # ============================================================
        # TIME BLOCK VALIDATION - Match session time_block to current period
        # ============================================================
        session_time_block = session.get('time_block')  # 'morning' or 'afternoon'
        current_period = time_check.get('period')  # 'morning' or 'afternoon'
        
        if session_time_block and session_time_block != current_period:
            period_names = {
                'morning': 'Morning (8:30 AM - 12:30 PM)',
                'afternoon': 'Afternoon (1:30 PM - 5:30 PM)'
            }
            
            print(f"🚫 TIME BLOCK MISMATCH: {session_time_block} session during {current_period} hours")
            return jsonify({
                'status': 'time_block_mismatch',
                'message': f'Cannot take attendance for {session_time_block} session during {current_period} hours',
                'session_time_block': session_time_block,
                'current_period': current_period,
                'current_time': time_check['current_time'],
                'allowed_periods': {
                    'morning_sessions': 'Only during 8:30 AM - 12:30 PM',
                    'afternoon_sessions': 'Only during 1:30 PM - 5:30 PM'
                },
                'suggestion': f'This {session_time_block} session can only be used during {period_names.get(session_time_block, session_time_block)} hours'
            }), 403
        
        print(f"✓ Time block validated: {session_time_block} session during {current_period} hours")
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
            student_result = db.execute_query('SELECT * FROM students WHERE student_id = %s', (student_id,))
            
            if not student_result:
                print(f"✗ Student not in database: {student_id}")
                return jsonify({
                    'status': 'unknown',
                    'message': f'Student {student_id} not found in database'
                }), 200
            
            student = student_result[0]  # Get the first result
            
            # ============================================================
            # VALIDATE STUDENT SECTION/YEAR MATCHES SESSION
            # ============================================================
            student_section = student.get('section', '')
            student_year = student.get('year', '')
            session_section = session.get('section_id', '')
            session_year = session.get('year', '')
            
            if student_section != session_section or student_year != session_year:
                print(f"✗ SECTION/YEAR MISMATCH:")
                print(f"  Student: {student.get('name')} ({student_id})")
                print(f"  Student Section/Year: {student_section}, {student_year}")
                print(f"  Session Section/Year: {session_section}, {session_year}")
                print(f"  → REJECTED: Student not in this class")
                sys.stdout.flush()
                
                return jsonify({
                    'status': 'wrong_section',
                    'message': f'{student.get("name")} is not in this class (Section {student_section}, {student_year})',
                    'student_id': student_id,
                    'student_name': student.get('name'),
                    'student_section': student_section,
                    'student_year': student_year,
                    'session_section': session_section,
                    'session_year': session_year
                }), 200
            
            print(f"✓ Section/Year validated: {student_section}, {student_year}")
            
            # ============================================================
            # ULTRA-STRICT DUPLICATE PREVENTION FOR SINGLE SESSION
            # ============================================================
            # Check for ANY existing attendance record in this session (present OR absent)
            # This ensures ONE attendance record per student per session, period.
            
            existing_result = db.execute_query(
                '''SELECT * FROM attendance 
                   WHERE student_id = %s 
                   AND session_id = %s 
                   ORDER BY timestamp DESC
                   LIMIT 1''',
                (student_id, session_id)
            )
            existing = existing_result[0] if existing_result else None
            
            if existing:
                # Student already has a record in this session
                existing_time = existing.get('timestamp')
                existing_status = existing.get('status')
                existing_confidence = existing.get('confidence', 0)
                time_diff = get_ethiopian_time() - existing_time if existing_time else timedelta(0)
                
                print(f"🚫 DUPLICATE BLOCKED: {student.get('name')} already has attendance in session {session_id}")
                print(f"   Existing: {existing_status} at {existing_time} (confidence: {existing_confidence:.1f}%)")
                print(f"   New attempt: present at {get_ethiopian_time()} (confidence: {confidence:.1f}%)")
                print(f"   Time difference: {time_diff.total_seconds():.1f} seconds")
                
                # If existing record is 'absent' and new is 'present' with higher confidence, update to present
                if existing_status == 'absent' and confidence > 50:
                    new_confidence = max(confidence, existing_confidence)
                    db.execute_query(
                        'UPDATE attendance SET status = %s, confidence = %s, timestamp = %s WHERE id = %s',
                        ('present', new_confidence, get_ethiopian_time(), existing['id']),
                        fetch=False
                    )
                    
                    print(f"✓ Updated absent → present: confidence {existing_confidence:.1f}% → {new_confidence:.1f}%")
                    
                    return jsonify({
                        'status': 'updated_to_present',
                        'message': f'{student.get("name")} updated from absent to present',
                        'student_id': student_id,
                        'student_name': student.get('name'),
                        'confidence': new_confidence,
                        'previous_status': existing_status,
                        'action': 'absent_to_present'
                    }), 200
                
                # If existing record is 'present', just update confidence if higher
                elif existing_status == 'present':
                    if confidence > existing_confidence:
                        db.execute_query(
                            'UPDATE attendance SET confidence = %s, timestamp = %s WHERE id = %s',
                            (confidence, get_ethiopian_time(), existing['id']),
                            fetch=False
                        )
                        
                        print(f"✓ Updated confidence: {existing_confidence:.1f}% → {confidence:.1f}%")
                        
                        return jsonify({
                            'status': 'confidence_updated',
                            'message': f'{student.get("name")} confidence updated (already present)',
                            'student_id': student_id,
                            'student_name': student.get('name'),
                            'confidence': confidence,
                            'previous_confidence': existing_confidence,
                            'action': 'confidence_improved'
                        }), 200
                    else:
                        print(f"✓ No update needed: existing confidence {existing_confidence:.1f}% >= new {confidence:.1f}%")
                        
                        return jsonify({
                            'status': 'already_present',
                            'message': f'{student.get("name")} already marked present',
                            'student_id': student_id,
                            'student_name': student.get('name'),
                            'confidence': existing_confidence,
                            'time_since_last': f"{time_diff.total_seconds():.1f}s",
                            'action': 'no_change_needed'
                        }), 200
                
                # Any other case - block duplicate
                return jsonify({
                    'status': 'duplicate_blocked',
                    'message': f'{student.get("name")} already has attendance record in this session',
                    'student_id': student_id,
                    'student_name': student.get('name'),
                    'existing_status': existing_status,
                    'existing_confidence': existing_confidence,
                    'action': 'blocked_duplicate'
                }), 200
            
            print(f"✓ No existing record found - creating new attendance record")
            
            # Record NEW attendance entry with instructor_id, section_id, session_type, and time_block
            today = date.today().isoformat()
            attendance_doc = {
                'student_id': student_id,
                'session_id': session_id,
                'instructor_id': session.get('instructor_id'),
                'section_id': session.get('section_id', ''),
                'year': session.get('year', ''),
                'session_type': session.get('session_type', ''),  # 'lab' or 'theory'
                'time_block': session.get('time_block', ''),  # 'morning' or 'afternoon'
                'course_name': session.get('course_name', ''),
                'class_year': session.get('class_year', ''),
                'timestamp': get_ethiopian_time(),
                'date': today,
                'confidence': confidence,
                'status': 'present'
            }
            
            try:
                db.execute_query(
                    '''INSERT INTO attendance 
                       (student_id, session_id, instructor_id, section_id, year, 
                        session_type, time_block, course_name, class_year, 
                        timestamp, date, confidence, status) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                    (attendance_doc['student_id'], attendance_doc['session_id'], 
                     attendance_doc['instructor_id'], attendance_doc['section_id'], 
                     attendance_doc['year'], attendance_doc['session_type'], 
                     attendance_doc['time_block'], attendance_doc['course_name'], 
                     attendance_doc['class_year'], attendance_doc['timestamp'], 
                     attendance_doc['date'], attendance_doc['confidence'], 
                     attendance_doc['status']),
                    fetch=False
                )
            except Exception as e:
                # Handle database constraint violation (duplicate key)
                if "Duplicate entry" in str(e) or "1062" in str(e):
                    print(f"🚫 DATABASE CONSTRAINT: Duplicate prevented by unique constraint")
                    print(f"   Student: {student.get('name')} ({student_id})")
                    print(f"   Session: {session_id}")
                    print(f"   → Updating existing record instead")
                    
                    # Update existing record
                    db.execute_query(
                        '''UPDATE attendance 
                           SET confidence = GREATEST(confidence, %s), 
                               timestamp = %s 
                           WHERE student_id = %s AND session_id = %s''',
                        (confidence, get_ethiopian_time(), student_id, session_id),
                        fetch=False
                    )
                    
                    return jsonify({
                        'status': 'duplicate_prevented',
                        'message': f'{student.get("name")} already marked (database constraint)',
                        'student_id': student_id,
                        'student_name': student.get('name'),
                        'confidence': confidence,
                        'action': 'constraint_prevented'
                    }), 200
                else:
                    # Re-raise other database errors
                    raise e
            
            # Update session count (only for NEW entries)
            db.execute_query(
                'UPDATE sessions SET attendance_count = attendance_count + 1 WHERE id = %s',
                (session_id,),
                fetch=False
            )
            
            print(f"✓ NEW attendance recorded: {student.get('name')}")
            print("="*80 + "\n")
            sys.stdout.flush()
            
            return jsonify({
                'status': 'recognized',
                'student_id': student_id,
                'student_name': student.get('name'),
                'confidence': confidence,
                'message': f'Attendance recorded for {student.get("name")}',
                'new_entry': True
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
    """Start a new attendance session with time block"""
    try:
        # ============================================================
        # WORKING HOURS VALIDATION
        # ============================================================
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from utils.time_restrictions import is_within_working_hours
        
        time_check = is_within_working_hours()
        
        if not time_check['allowed']:
            print(f"🚫 SESSION START BLOCKED: Outside working hours - {time_check['message']}")
            return jsonify({
                'error': 'Outside working hours',
                'message': time_check['message'],
                'current_time': time_check['current_time'],
                'next_period': time_check['next_period'],
                'minutes_until_next': time_check.get('minutes_until_next', 0),
                'working_hours': {
                    'morning': '8:30 AM - 12:30 PM',
                    'afternoon': '1:30 PM - 5:30 PM',
                    'lunch_break': '12:30 PM - 1:30 PM (blocked)'
                }
            }), 403
        
        print(f"✅ SESSION START OK: {time_check['message']}")
        
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate time_block matches current time period
        time_block = data.get('time_block')
        if time_block:
            current_period = time_check.get('period')  # 'morning' or 'afternoon'
            
            if time_block != current_period:
                period_names = {
                    'morning': 'Morning (8:30 AM - 12:30 PM)',
                    'afternoon': 'Afternoon (1:30 PM - 5:30 PM)'
                }
                
                print(f"🚫 TIME BLOCK MISMATCH: Trying to create {time_block} session during {current_period} hours")
                return jsonify({
                    'error': 'Time block mismatch',
                    'message': f'Cannot create {time_block} session during {current_period} hours',
                    'current_period': current_period,
                    'current_time': time_check['current_time'],
                    'requested_time_block': time_block,
                    'allowed_time_blocks': {
                        'morning': 'Only during 8:30 AM - 12:30 PM',
                        'afternoon': 'Only during 1:30 PM - 5:30 PM'
                    },
                    'suggestion': f'You can create {time_block} sessions during {period_names.get(time_block, time_block)} hours'
                }), 403
        
        db = get_db()
        instructor_result = db.execute_query('SELECT * FROM users WHERE id = %s', (user_id,))
        
        if not instructor_result:
            return jsonify({'error': 'Instructor not found'}), 404
        
        instructor = instructor_result[0]  # Get the first result
        
        # Validate session_type is provided
        session_type = data.get('session_type')
        if not session_type or session_type not in ['lab', 'theory']:
            return jsonify({
                'error': 'Invalid session type',
                'message': 'session_type must be "lab" or "theory"'
            }), 400
        
        # Validate time_block is provided
        time_block = data.get('time_block')
        if not time_block or time_block not in ['morning', 'afternoon']:
            return jsonify({
                'error': 'Invalid time block',
                'message': 'time_block must be "morning" or "afternoon"'
            }), 400
        
        # Parse instructor session types from JSON
        import json
        instructor_session_types = []
        if instructor.get('session_types'):
            try:
                instructor_session_types = json.loads(instructor['session_types'])
            except (json.JSONDecodeError, TypeError):
                instructor_session_types = []
        
        # Validate instructor has access to this session type
        if session_type not in instructor_session_types:
            return jsonify({
                'error': 'Unauthorized session type',
                'message': f'You do not have access to {session_type} sessions'
            }), 403
        
        # Validate section and year are provided
        section_id = data.get('section_id', '')
        year = data.get('year', '')
        
        if not section_id:
            return jsonify({
                'error': 'Section required',
                'message': 'Please provide a section'
            }), 400
        
        if not year:
            return jsonify({
                'error': 'Year required',
                'message': 'Please provide a year'
            }), 400
        
        # Get course from request data, fallback to instructor's first course
        course = data.get('course', '') or instructor.get('course_name', '')
        
        session_doc = {
            'instructor_id': user_id,
            'instructor_name': instructor.get('name', 'Unknown'),
            'section_id': section_id,
            'year': year,
            'session_type': session_type,  # 'lab' or 'theory'
            'time_block': time_block,  # 'morning' or 'afternoon'
            'course_name': course,  # Use the selected course from the form
            'class_year': instructor.get('class_year', ''),
            'name': data.get('name', f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"),
            'course': course,  # Store in both fields for compatibility
            'start_time': get_ethiopian_time(),
            'end_time': None,
            'status': 'active',
            'attendance_count': 0,
            'present_students': [],  # Track present students
            'absent_students': []    # Track absent students (if needed)
        }
        
        session_id = db.execute_query(
            '''INSERT INTO sessions 
               (instructor_id, instructor_name, section_id, year, 
                session_type, time_block, course_name, class_year, 
                name, start_time, status, attendance_count) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
            (session_doc['instructor_id'], session_doc['instructor_name'], 
             session_doc['section_id'], session_doc['year'], 
             session_doc['session_type'], session_doc['time_block'], 
             session_doc['course_name'], session_doc['class_year'], 
             session_doc['name'], session_doc['start_time'], 
             session_doc['status'], session_doc['attendance_count']),
            fetch=False
        )
        
        print(f"✅ Session started: {session_type} - {time_block} - {session_doc['name']}")
        
        return jsonify({
            'message': 'Session started successfully',
            'session_id': str(session_id),
            'session': {
                'id': str(session_id),
                'name': session_doc['name'],
                'session_type': session_type,
                'time_block': time_block,
                'section_id': section_id,
                'year': year,
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
    """End an attendance session - only instructor's own sessions"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'session_id' not in data:
            return jsonify({'error': 'Session ID required'}), 400
        
        db = get_db()
        
        # Verify session belongs to this instructor
        session_result = db.execute_query('SELECT * FROM sessions WHERE id = %s', (data['session_id'],))
        session = session_result[0] if session_result else None
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        if str(session.get('instructor_id')) != str(user_id):
            return jsonify({
                'error': 'Unauthorized',
                'message': 'You can only end your own sessions'
            }), 403
        
        # Check if this is a permanent end (semester end) or daily stop
        end_type = data.get('end_type', 'semester')  # 'daily' or 'semester'
        
        if end_type == 'daily':
            # Stop camera for the day - can be reopened after 12 hours
            db.execute_query(
                'UPDATE sessions SET end_time = %s, status = %s WHERE id = %s',
                (get_ethiopian_time(), 'stopped_daily', data['session_id']),
                fetch=False
            )
            logger.info(f"Session {data['session_id']} stopped for the day")
            return jsonify({'message': 'Session stopped for the day. Can be reopened after 12 hours.'}), 200
        else:
            # ============================================================
            # SEMESTER END RESTRICTIONS
            # ============================================================
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from utils.time_restrictions import check_semester_end_eligibility
            
            # Get instructor's first session date and total session count
            first_session_result = db.execute_query(
                '''SELECT MIN(start_time) as first_session_date, COUNT(*) as session_count
                   FROM sessions 
                   WHERE instructor_id = %s 
                   AND course_name = %s 
                   AND section_id = %s 
                   AND year = %s''',
                (user_id, session.get('course_name'), session.get('section_id'), session.get('year'))
            )
            
            if first_session_result and first_session_result[0]['first_session_date']:
                first_session_date = first_session_result[0]['first_session_date']
                session_count = first_session_result[0]['session_count']
                
                eligibility = check_semester_end_eligibility(first_session_date, session_count)
                
                if not eligibility['can_end_semester']:
                    print(f"🚫 SEMESTER END BLOCKED: {eligibility['message']}")
                    return jsonify({
                        'error': 'Cannot end semester',
                        'message': eligibility['message'],
                        'eligibility': eligibility,
                        'requirements': {
                            'minimum_months': 4,
                            'minimum_sessions': 8,
                            'current_months': eligibility['months_elapsed'],
                            'current_sessions': eligibility['sessions_conducted']
                        }
                    }), 403
                
                print(f"✅ SEMESTER END ALLOWED: {eligibility['message']}")
            
            # Permanent end for semester
            db.execute_query(
                'UPDATE sessions SET end_time = %s, status = %s WHERE id = %s',
                (get_ethiopian_time(), 'ended_semester', data['session_id']),
                fetch=False
            )
            logger.info(f"Session {data['session_id']} ended permanently")
            return jsonify({'message': 'Session ended permanently for semester'}), 200
    
    except Exception as e:
        logger.error(f"Error ending session: {e}", exc_info=True)
        return jsonify({
            'error': 'Failed to end session',
            'message': str(e)
        }), 500


@attendance_bp.route('/admin-reopen-session', methods=['POST'])
@jwt_required()
@role_required('admin')
def admin_reopen_session():
    """Admin-only: Reopen session with time block restrictions"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'session_id' not in data:
            return jsonify({'error': 'Session ID required'}), 400
        
        session_id = data['session_id']
        db = get_db()
        
        # Get session details
        session_result = db.execute_query('SELECT * FROM sessions WHERE id = %s', (session_id,))
        if not session_result:
            return jsonify({'error': 'Session not found'}), 404
        
        session = session_result[0]
        
        # ============================================================
        # TIME BLOCK VALIDATION - Check if current time matches session's time block
        # ============================================================
        
        # Check current time restrictions
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from utils.time_restrictions import is_within_working_hours
        
        time_check = is_within_working_hours()
        if not time_check['allowed']:
            print(f"🚫 BLOCKED: Cannot reopen session outside working hours - {time_check['message']}")
            return jsonify({
                'error': 'Outside working hours',
                'message': time_check['message'],
                'current_time': time_check['current_time'],
                'working_hours': {
                    'morning': '8:30 AM - 12:30 PM',
                    'afternoon': '1:30 PM - 5:30 PM'
                }
            }), 403
        
        # Get session's original time block
        session_time_block = session.get('time_block')  # 'morning' or 'afternoon'
        current_period = time_check.get('period')  # 'morning' or 'afternoon'
        
        if session_time_block and session_time_block != current_period:
            period_names = {
                'morning': 'Morning (8:30 AM - 12:30 PM)',
                'afternoon': 'Afternoon (1:30 PM - 5:30 PM)'
            }
            
            print(f"🚫 TIME BLOCK MISMATCH: Cannot reopen {session_time_block} session during {current_period} hours")
            return jsonify({
                'error': 'Time block mismatch',
                'message': f'Cannot reopen {session_time_block} session during {current_period} hours',
                'session_time_block': session_time_block,
                'current_period': current_period,
                'current_time': time_check['current_time'],
                'allowed_reopen_times': {
                    'morning_sessions': 'Only during 8:30 AM - 12:30 PM',
                    'afternoon_sessions': 'Only during 1:30 PM - 5:30 PM'
                },
                'suggestion': f'This {session_time_block} session can only be reopened during {period_names.get(session_time_block, session_time_block)} hours'
            }), 403
        
        print(f"✓ Time block validated: Reopening {session_time_block} session during {current_period} hours")
        print(f"🔧 Admin {user_id} reopening session {session_id} (status: {session.get('status')})")
        
        # Reopen the session
        db.execute_query(
            'UPDATE sessions SET status = %s, end_time = NULL WHERE id = %s',
            ('active', session_id),
            fetch=False
        )
        
        # Log the admin action
        print(f"✅ Admin reopened session {session_id} - Status changed to 'active'")
        
        return jsonify({
            'message': f'Session reopened successfully',
            'session_id': session_id,
            'previous_status': session.get('status'),
            'new_status': 'active',
            'time_block': session_time_block,
            'current_period': current_period
        }), 200
        
    except Exception as e:
        print(f"❌ Error in admin reopen session: {e}")
        return jsonify({
            'error': 'Failed to reopen session',
            'message': str(e)
        }), 500


@attendance_bp.route('/instructor-reopen-session', methods=['POST'])
@jwt_required()
@role_required('instructor')
def instructor_reopen_session():
    """Instructor: Reopen their own session with time block restrictions"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'session_id' not in data:
            return jsonify({'error': 'Session ID required'}), 400
        
        session_id = data['session_id']
        db = get_db()
        
        # Get session details and verify ownership
        session_result = db.execute_query('SELECT * FROM sessions WHERE id = %s', (session_id,))
        if not session_result:
            return jsonify({'error': 'Session not found'}), 404
        
        session = session_result[0]
        
        # Verify instructor owns this session
        if str(session.get('instructor_id')) != str(user_id):
            return jsonify({'error': 'You can only reopen your own sessions'}), 403
        
        # Allow reopening of stopped_daily and completed sessions
        if session.get('status') not in ['stopped_daily', 'completed']:
            return jsonify({
                'error': 'Invalid session status',
                'message': 'Only daily stopped or completed sessions can be reopened by instructors',
                'current_status': session.get('status')
            }), 400
        
        # ============================================================
        # TIME BLOCK VALIDATION - Check if current time matches session's time block
        # ============================================================
        
        # Check current time restrictions
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from utils.time_restrictions import is_within_working_hours
        
        time_check = is_within_working_hours()
        if not time_check['allowed']:
            print(f"🚫 BLOCKED: Cannot reopen session outside working hours - {time_check['message']}")
            return jsonify({
                'error': 'Outside working hours',
                'message': time_check['message'],
                'current_time': time_check['current_time'],
                'working_hours': {
                    'morning': '8:30 AM - 12:30 PM',
                    'afternoon': '1:30 PM - 5:30 PM'
                }
            }), 403
        
        # Get session's original time block
        session_time_block = session.get('time_block')  # 'morning' or 'afternoon'
        current_period = time_check.get('period')  # 'morning' or 'afternoon'
        
        if session_time_block and session_time_block != current_period:
            period_names = {
                'morning': 'Morning (8:30 AM - 12:30 PM)',
                'afternoon': 'Afternoon (1:30 PM - 5:30 PM)'
            }
            
            print(f"🚫 TIME BLOCK MISMATCH: Cannot reopen {session_time_block} session during {current_period} hours")
            return jsonify({
                'error': 'Time block mismatch',
                'message': f'Cannot reopen {session_time_block} session during {current_period} hours',
                'session_time_block': session_time_block,
                'current_period': current_period,
                'current_time': time_check['current_time'],
                'allowed_reopen_times': {
                    'morning_sessions': 'Only during 8:30 AM - 12:30 PM',
                    'afternoon_sessions': 'Only during 1:30 PM - 5:30 PM'
                },
                'suggestion': f'This {session_time_block} session can only be reopened during {period_names.get(session_time_block, session_time_block)} hours'
            }), 403
        
        print(f"✓ Time block validated: Reopening {session_time_block} session during {current_period} hours")
        print(f"🔧 Instructor {user_id} reopening session {session_id} (status: {session.get('status')})")
        
        # Reopen the session
        db.execute_query(
            'UPDATE sessions SET status = %s, end_time = NULL WHERE id = %s',
            ('active', session_id),
            fetch=False
        )
        
        # Log the instructor action
        print(f"✅ Instructor reopened session {session_id} - Status changed to 'active'")
        
        return jsonify({
            'message': f'Session reopened successfully',
            'session_id': session_id,
            'previous_status': session.get('status'),
            'new_status': 'active',
            'time_block': session_time_block,
            'current_period': current_period
        }), 200
        
    except Exception as e:
        print(f"❌ Error in instructor reopen session: {e}")
        return jsonify({
            'error': 'Failed to reopen session',
            'message': str(e)
        }), 500


@attendance_bp.route('/mark-absent', methods=['POST'])
@jwt_required()
@role_required('instructor')
def mark_absent_students():
    """Mark absent students when camera is stopped - also stops session for the day"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'session_id' not in data:
            return jsonify({'error': 'Session ID required'}), 400
        
        session_id = data['session_id']
        db = get_db()
        
        # Get session info
        session_result = db.execute_query('SELECT * FROM sessions WHERE id = %s', (session_id,))
        if not session_result:
            return jsonify({'error': 'Session not found'}), 404
        
        session = session_result[0]
        
        # Verify session belongs to this instructor
        if str(session.get('instructor_id')) != str(user_id):
            return jsonify({
                'error': 'Unauthorized',
                'message': 'You can only mark absents for your own sessions'
            }), 403
        
        # Get all students in this section and year
        all_students_result = db.execute_query(
            'SELECT student_id, name FROM students WHERE section = %s AND year = %s',
            (session.get('section_id'), session.get('year'))
        )
        
        if not all_students_result:
            return jsonify({
                'message': 'No students found in this section/year',
                'absent_count': 0
            }), 200
        
        # Get students who are already marked present TODAY
        today = date.today().isoformat()
        present_students_result = db.execute_query(
            'SELECT DISTINCT student_id FROM attendance WHERE session_id = %s AND date = %s AND status = %s',
            (session_id, today, 'present')
        )
        
        present_student_ids = [row['student_id'] for row in present_students_result] if present_students_result else []
        
        # Mark absent students
        absent_count = 0
        for student in all_students_result:
            student_id = student['student_id']
            
            if student_id not in present_student_ids:
                # Mark as absent
                db.execute_query(
                    '''INSERT INTO attendance 
                       (student_id, session_id, instructor_id, section_id, year,
                        session_type, time_block, course_name, class_year,
                        timestamp, date, confidence, status) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                    (student_id, session_id, session.get('instructor_id'),
                     session.get('section_id'), session.get('year'),
                     session.get('session_type'), session.get('time_block'),
                     session.get('course_name'), session.get('class_year'),
                     get_ethiopian_time(), today, 0.0, 'absent'),
                    fetch=False
                )
                absent_count += 1
                logger.info(f"Marked {student_id} as absent for session {session_id}")
        
        # Stop session for the day (can be reopened)
        db.execute_query(
            'UPDATE sessions SET end_time = %s, status = %s WHERE id = %s',
            (get_ethiopian_time(), 'stopped_daily', session_id),
            fetch=False
        )
        
        logger.info(f"Marked {absent_count} students as absent and ended session {session_id}")
        
        return jsonify({
            'message': f'Successfully marked {absent_count} students as absent',
            'absent_count': absent_count,
            'total_students': len(all_students_result),
            'present_count': len(present_student_ids)
        }), 200
    
    except Exception as e:
        logger.error(f"Error marking absent students: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to mark absent students',
            'message': str(e)
        }), 500


@attendance_bp.route('/session/<session_id>', methods=['GET'])
@jwt_required()
@role_required('instructor', 'admin')
def get_session_attendance(session_id):
    """Get attendance for a specific session - instructors see only their sessions"""
    try:
        user_id = get_jwt_identity()
        db = get_db()
        
        # Get session info
        session_result = db.execute_query('SELECT * FROM sessions WHERE id = %s', (session_id,))
        if not session_result:
            return jsonify({'error': 'Session not found'}), 404
        
        session = session_result[0]
        
        # Get attendance records for this session
        attendance_result = db.execute_query(
            'SELECT * FROM attendance WHERE session_id = %s ORDER BY timestamp DESC',
            (session_id,)
        )
        
        # Build attendance list with student info
        attendance_list = []
        for record in attendance_result:
            student_result = db.execute_query('SELECT * FROM students WHERE student_id = %s', (record['student_id'],))
            student = student_result[0] if student_result else None
            
            attendance_list.append({
                'id': str(record['id']),
                'student_id': record['student_id'],
                'student_name': student['name'] if student else 'Unknown',
                'timestamp': record['timestamp'].isoformat() if record.get('timestamp') else None,
                'confidence': float(record.get('confidence', 0)) if record.get('confidence') else 0,
                'status': record.get('status', 'present')
            })
        
        return jsonify({
            'session': {
                'id': str(session['id']),
                'name': session.get('name', 'Unknown Session'),
                'instructor_name': session.get('instructor_name', 'Unknown'),
                'section_id': session.get('section_id', ''),
                'year': session.get('year', ''),
                'session_type': session.get('session_type', ''),
                'time_block': session.get('time_block', ''),
                'course_name': session.get('course_name', ''),
                'start_time': session['start_time'].isoformat() if session.get('start_time') else None,
                'end_time': session['end_time'].isoformat() if session.get('end_time') else None,
                'status': session.get('status', 'unknown'),
                'attendance_count': session.get('attendance_count', 0)
            },
            'attendance': attendance_list
        }), 200
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to get session attendance',
            'message': str(e)
        }), 500


@attendance_bp.route('/check-semester-eligibility', methods=['POST'])
@jwt_required()
@role_required('instructor')
def check_semester_eligibility():
    """Check if instructor can end semester for a specific course/section"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        course_name = data.get('course_name')
        section_id = data.get('section_id')
        year = data.get('year')
        
        if not all([course_name, section_id, year]):
            return jsonify({
                'error': 'Missing required fields',
                'message': 'course_name, section_id, and year are required'
            }), 400
        
        db = get_db()
        
        # Get instructor's first session date and total session count for this course/section
        result = db.execute_query(
            '''SELECT MIN(start_time) as first_session_date, COUNT(*) as session_count
               FROM sessions 
               WHERE instructor_id = %s 
               AND course_name = %s 
               AND section_id = %s 
               AND year = %s''',
            (user_id, course_name, section_id, year)
        )
        
        if not result or not result[0]['first_session_date']:
            return jsonify({
                'can_end_semester': False,
                'message': 'No sessions found for this course/section',
                'sessions_conducted': 0,
                'months_elapsed': 0
            }), 200
        
        first_session_date = result[0]['first_session_date']
        session_count = result[0]['session_count']
        
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from utils.time_restrictions import check_semester_end_eligibility
        eligibility = check_semester_end_eligibility(first_session_date, session_count)
        
        return jsonify(eligibility), 200
        
    except Exception as e:
        logger.error(f"Error checking semester eligibility: {e}", exc_info=True)
        return jsonify({
            'error': 'Failed to check eligibility',
            'message': str(e)
        }), 500


@attendance_bp.route('/sessions', methods=['GET'])
@jwt_required()
@role_required('instructor', 'admin')
def get_sessions():
    """Get all sessions with reopen eligibility"""
    try:
        user_id = get_jwt_identity()
        db = get_db()
        
        user_result = db.execute_query('SELECT * FROM users WHERE id = %s', (user_id,))
        user = user_result[0] if user_result else None
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Build query based on user role
        print(f"🔍 User role: {user['role']}, User ID: {user_id}")
        
        if user['role'] == 'instructor':
            sessions = db.execute_query('SELECT * FROM sessions WHERE instructor_id = %s ORDER BY start_time DESC', (user_id,))
            print(f"📊 Found {len(sessions)} sessions for instructor {user_id}")
        else:
            sessions = db.execute_query('SELECT * FROM sessions ORDER BY start_time DESC')
            print(f"📊 Found {len(sessions)} total sessions for admin")
        

        session_list = []
        for session in sessions:
            # Check if session can be reopened (stopped for 12+ hours)
            can_reopen = False
            hours_until_reopen = None
            
            if session.get('status') in ['stopped_daily', 'completed'] and session.get('end_time'):
                hours_since_stop = (datetime.utcnow() - session['end_time']).total_seconds() / 3600
                if hours_since_stop >= 12:
                    can_reopen = True
                else:
                    hours_until_reopen = 12 - hours_since_stop
            
            session_data = {
                'id': session['id'],  # Keep as integer
                'name': session.get('name', 'Unknown Session'),
                'instructor_name': session.get('instructor_name', 'Unknown'),
                'course_name': session.get('course_name', ''),
                'section_id': session.get('section_id', ''),
                'year': session.get('year', ''),
                'session_type': session.get('session_type', ''),
                'time_block': session.get('time_block', ''),
                'start_time': session['start_time'].isoformat() if session.get('start_time') else None,
                'end_time': session['end_time'].isoformat() if session.get('end_time') else None,
                'status': session.get('status', 'unknown'),
                'attendance_count': session.get('attendance_count', 0),
                'can_reopen': can_reopen,
                'hours_until_reopen': hours_until_reopen
            }
            
            print(f"📊 Session {session['id']}: {session_data['name']} - Status: {session_data['status']}")
            session_list.append(session_data)
        
        return jsonify({
            'sessions': session_list,
            'total': len(session_list)
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting sessions: {e}", exc_info=True)
        return jsonify({
            'error': 'Failed to get sessions',
            'message': str(e)
        }), 500
