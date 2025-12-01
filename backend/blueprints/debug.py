from flask import Blueprint, request, jsonify
from recognizer.classifier import face_recognizer
from recognizer.loader import model_loader
import os
from config import config

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/echo', methods=['GET', 'POST'])
def echo():
    """Simple echo endpoint for testing"""
    if request.method == 'GET':
        return jsonify({
            'message': 'SmartAttendance API is running',
            'method': 'GET',
            'timestamp': str(datetime.utcnow())
        }), 200
    else:
        data = request.get_json() or {}
        return jsonify({
            'message': 'Echo response',
            'received': data,
            'method': 'POST'
        }), 200

@debug_bp.route('/recognition-test', methods=['POST'])
def recognition_test():
    """Test face recognition without recording attendance"""
    if 'image' not in request.files and 'image' not in request.form:
        return jsonify({'error': 'No image provided'}), 400
    
    # Get image data
    if 'image' in request.files:
        image_file = request.files['image']
        image_data = image_file.read()
    else:
        image_data = request.form.get('image')
    
    # Test recognition
    result = face_recognizer.recognize(image_data)
    
    return jsonify({
        'test_mode': True,
        'result': result
    }), 200

@debug_bp.route('/model-status', methods=['GET'])
def model_status():
    """Check model loading status"""
    model_path = config.MODEL_PATH
    
    files_status = {
        'classifier': os.path.exists(os.path.join(model_path, 'face_classifier_v1.pkl')),
        'label_encoder': os.path.exists(os.path.join(model_path, 'label_encoder.pkl')),
        'label_classes': os.path.exists(os.path.join(model_path, 'label_encoder_classes.npy'))
    }
    
    return jsonify({
        'model_loaded': model_loader.is_loaded(),
        'model_path': model_path,
        'files': files_status,
        'threshold': config.RECOGNITION_CONFIDENCE_THRESHOLD
    }), 200

@debug_bp.route('/reload-models', methods=['POST'])
def reload_models():
    """Force reload models"""
    success = model_loader.load_models()
    
    return jsonify({
        'success': success,
        'model_loaded': model_loader.is_loaded()
    }), 200 if success else 500

from datetime import datetime
