"""
Instructor-specific endpoints for records, settings, and exports
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime
from utils.security import role_required, hash_password, verify_password
from db.mongo import get_db
import csv
import io
import logging

instructor_bp = Blueprint('instructor', __name__)
logger = logging.getLogger(__name__)


@instructor_bp.route('/records', methods=['GET'])
@jwt_required()
@role_required('instructor', 'admin')
def get_attendance_records():
    """
    Get attendance records with filtering - instructors see ONLY their records
    Query params: start_date, end_date, student_id, session_id
    """
    try:
        user_id = get_jwt_identity()
        db = get_db()
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        student_id = request.args.get('student_id')
        session_id = request.args.get('session_id')
        
        # Build query
        query = {}
        
        # CRITICAL: Filter by instructor_id for instructors (admins see all)
        user = db.users.find_one({'_id': ObjectId(user_id)})
        if user['role'] == 'instructor':
            # Direct filter on attendance records by instructor_id
            query['instructor_id'] = user_id
            logger.info(f"Instructor {user_id} - filtering by instructor_id")
        
        # Date range filter
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query['$gte'] = start_date
            if end_date:
                date_query['$lte'] = end_date
            if date_query:
                query['date'] = date_query
        
        # Student filter
        if student_id:
            query['student_id'] = student_id
        
        # Session filter
        if session_id:
            query['session_id'] = session_id
        
        logger.info(f"Fetching records with query: {query}")
        
        # Get records
        records = list(db.attendance.find(query).sort('timestamp', -1).limit(1000))
        
        result = []
        for record in records:
            student = db.students.find_one({'student_id': record['student_id']})
            session = db.sessions.find_one({'_id': ObjectId(record['session_id'])})
            
            result.append({
                'id': str(record['_id']),
                'student_id': record['student_id'],
                'student_name': student['name'] if student else 'Unknown',
                'session_id': record['session_id'],
                'session_name': session['name'] if session else 'Unknown',
                'section_id': record.get('section_id', ''),
                'year': record.get('year', ''),
                'course_name': record.get('course_name', ''),
                'session_type': record.get('session_type', ''),
                'date': record['date'],
                'timestamp': record['timestamp'].isoformat(),
                'confidence': record.get('confidence', 0),
                'status': record.get('status', 'present')
            })
        
        logger.info(f"Returning {len(result)} records for instructor {user_id}")
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error fetching records: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch records', 'message': str(e)}), 500


@instructor_bp.route('/records/export/csv', methods=['GET'])
@jwt_required()
@role_required('instructor', 'admin')
def export_csv():
    """Export attendance records to CSV - instructors see ONLY their records"""
    try:
        user_id = get_jwt_identity()
        db = get_db()
        
        # Get same filters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        student_id = request.args.get('student_id')
        session_id = request.args.get('session_id')
        
        # Build query (same as get_attendance_records)
        query = {}
        user = db.users.find_one({'_id': ObjectId(user_id)})
        if user['role'] == 'instructor':
            # CRITICAL: Filter by instructor_id
            query['instructor_id'] = user_id
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query['$gte'] = start_date
            if end_date:
                date_query['$lte'] = end_date
            if date_query:
                query['date'] = date_query
        
        if student_id:
            query['student_id'] = student_id
        if session_id:
            query['session_id'] = session_id
        
        # Get records
        records = list(db.attendance.find(query).sort('timestamp', -1))
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Date', 'Time', 'Student ID', 'Student Name', 'Session', 'Confidence', 'Status'])
        
        # Write data
        for record in records:
            student = db.students.find_one({'student_id': record['student_id']})
            session = db.sessions.find_one({'_id': ObjectId(record['session_id'])})
            
            writer.writerow([
                record['date'],
                record['timestamp'].strftime('%H:%M:%S'),
                record['student_id'],
                student['name'] if student else 'Unknown',
                session['name'] if session else 'Unknown',
                f"{record.get('confidence', 0):.2%}",
                record.get('status', 'present')
            ])
        
        # Create response
        output.seek(0)
        csv_data = output.getvalue()
        
        # Create BytesIO for send_file
        csv_bytes = io.BytesIO(csv_data.encode('utf-8'))
        csv_bytes.seek(0)
        
        filename = f'attendance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return send_file(
            csv_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        logger.error(f"Error exporting CSV: {e}", exc_info=True)
        return jsonify({'error': 'Failed to export CSV', 'message': str(e)}), 500


@instructor_bp.route('/records/export/excel', methods=['GET'])
@jwt_required()
@role_required('instructor', 'admin')
def export_excel():
    """Export attendance records to Excel - instructors see ONLY their records"""
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill
        
        user_id = get_jwt_identity()
        db = get_db()
        
        # Get same filters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        student_id = request.args.get('student_id')
        session_id = request.args.get('session_id')
        
        # Build query
        query = {}
        user = db.users.find_one({'_id': ObjectId(user_id)})
        if user['role'] == 'instructor':
            # CRITICAL: Filter by instructor_id
            query['instructor_id'] = user_id
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query['$gte'] = start_date
            if end_date:
                date_query['$lte'] = end_date
            if date_query:
                query['date'] = date_query
        
        if student_id:
            query['student_id'] = student_id
        if session_id:
            query['session_id'] = session_id
        
        # Get records
        records = list(db.attendance.find(query).sort('timestamp', -1))
        
        # Create workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Attendance Records"
        
        # Style header
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        # Write header
        headers = ['Date', 'Time', 'Student ID', 'Student Name', 'Session', 'Confidence', 'Status']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
        
        # Write data
        for row_idx, record in enumerate(records, 2):
            student = db.students.find_one({'student_id': record['student_id']})
            session = db.sessions.find_one({'_id': ObjectId(record['session_id'])})
            
            ws.cell(row=row_idx, column=1, value=record['date'])
            ws.cell(row=row_idx, column=2, value=record['timestamp'].strftime('%H:%M:%S'))
            ws.cell(row=row_idx, column=3, value=record['student_id'])
            ws.cell(row=row_idx, column=4, value=student['name'] if student else 'Unknown')
            ws.cell(row=row_idx, column=5, value=session['name'] if session else 'Unknown')
            ws.cell(row=row_idx, column=6, value=f"{record.get('confidence', 0):.2%}")
            ws.cell(row=row_idx, column=7, value=record.get('status', 'present'))
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Save to BytesIO
        excel_bytes = io.BytesIO()
        wb.save(excel_bytes)
        excel_bytes.seek(0)
        
        filename = f'attendance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        return send_file(
            excel_bytes,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    
    except ImportError:
        return jsonify({'error': 'openpyxl not installed', 'message': 'Install with: pip install openpyxl'}), 500
    except Exception as e:
        logger.error(f"Error exporting Excel: {e}", exc_info=True)
        return jsonify({'error': 'Failed to export Excel', 'message': str(e)}), 500


@instructor_bp.route('/settings', methods=['GET'])
@jwt_required()
@role_required('instructor')
def get_settings():
    """Get instructor settings"""
    try:
        user_id = get_jwt_identity()
        db = get_db()
        
        settings = db.user_settings.find_one({'user_id': user_id})
        
        if not settings:
            # Return defaults
            return jsonify({
                'confidence_threshold': 0.60,
                'capture_interval': 2,
                'auto_capture': True
            }), 200
        
        return jsonify({
            'confidence_threshold': settings.get('confidence_threshold', 0.60),
            'capture_interval': settings.get('capture_interval', 2),
            'auto_capture': settings.get('auto_capture', True)
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching settings: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch settings', 'message': str(e)}), 500


@instructor_bp.route('/settings', methods=['PUT'])
@jwt_required()
@role_required('instructor')
def update_settings():
    """Update instructor settings"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        db = get_db()
        
        settings_doc = {
            'user_id': user_id,
            'confidence_threshold': float(data.get('confidence_threshold', 0.60)),
            'capture_interval': int(data.get('capture_interval', 2)),
            'auto_capture': bool(data.get('auto_capture', True)),
            'updated_at': datetime.utcnow()
        }
        
        db.user_settings.update_one(
            {'user_id': user_id},
            {'$set': settings_doc},
            upsert=True
        )
        
        logger.info(f"Settings updated for user {user_id}")
        return jsonify({'message': 'Settings updated successfully'}), 200
    
    except Exception as e:
        logger.error(f"Error updating settings: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update settings', 'message': str(e)}), 500


@instructor_bp.route('/change-password', methods=['PUT'])
@jwt_required()
@role_required('instructor')
def change_password():
    """Change instructor password"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        db = get_db()
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Both current and new password required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters'}), 400
        
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not verify_password(current_password, user['password']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'password': hash_password(new_password)}}
        )
        
        logger.info(f"Password changed for user {user_id}")
        return jsonify({'message': 'Password changed successfully'}), 200
    
    except Exception as e:
        logger.error(f"Error changing password: {e}", exc_info=True)
        return jsonify({'error': 'Failed to change password', 'message': str(e)}), 500


@instructor_bp.route('/sections', methods=['GET'])
@jwt_required()
@role_required('instructor')
def get_instructor_sections():
    """Get instructor's assigned sections"""
    try:
        user_id = get_jwt_identity()
        db = get_db()
        
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        sections = user.get('sections', [])
        
        return jsonify({
            'sections': sections,
            'instructor_name': user.get('name', 'Unknown')
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching sections: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch sections', 'message': str(e)}), 500


@instructor_bp.route('/info', methods=['GET'])
@jwt_required()
@role_required('instructor')
def get_instructor_info():
    """Get instructor's information including session types"""
    try:
        user_id = get_jwt_identity()
        db = get_db()
        
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user:
            return jsonify({'error': 'Instructor not found'}), 404
        
        return jsonify({
            'name': user.get('name', 'Unknown'),
            'email': user.get('email', ''),
            'department': user.get('department', ''),
            'course_name': user.get('course_name', ''),
            'class_year': user.get('class_year', ''),
            'session_types': user.get('session_types', []),  # ['lab'], ['theory'], or ['lab', 'theory']
            'sections': user.get('sections', [])
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching instructor info: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch instructor info', 'message': str(e)}), 500


@instructor_bp.route('/students', methods=['GET'])
@jwt_required()
@role_required('instructor', 'admin')
def get_students_list():
    """Get list of students - instructors see only students from their attendance records"""
    try:
        user_id = get_jwt_identity()
        db = get_db()
        
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if user['role'] == 'instructor':
            # Get unique student IDs from instructor's attendance records
            attendance_records = db.attendance.find(
                {'instructor_id': user_id},
                {'student_id': 1}
            )
            student_ids = list(set(record['student_id'] for record in attendance_records))
            
            # Get student details
            students = list(db.students.find(
                {'student_id': {'$in': student_ids}},
                {'student_id': 1, 'name': 1}
            ).sort('student_id', 1))
        else:
            # Admins see all students
            students = list(db.students.find({}, {'student_id': 1, 'name': 1}).sort('student_id', 1))
        
        result = [
            {
                'student_id': s['student_id'],
                'name': s['name']
            }
            for s in students
        ]
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error fetching students: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch students', 'message': str(e)}), 500
