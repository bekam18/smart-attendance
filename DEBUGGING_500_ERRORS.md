# Debugging 500 Errors in Face Recognition API

Complete guide to diagnose and fix 500 Internal Server Errors in the `/api/attendance/recognize` endpoint.

## 🔍 Common Causes

### 1. Missing Dependencies
```python
# Missing: torch, torchvision, facenet-pytorch
ModuleNotFoundError: No module named 'torch'
ModuleNotFoundError: No module named 'facenet_pytorch'
```

### 2. Model Not Loaded
```python
# Model files exist but not loaded into memory
AttributeError: 'NoneType' object has no attribute 'predict'
```

### 3. MTCNN Initialization Failure
```python
# MTCNN fails to initialize on first request
RuntimeError: MTCNN initialization failed
```

### 4. Image Processing Errors
```python
# Base64 decoding, format conversion issues
ValueError: invalid literal for int() with base 16
PIL.UnidentifiedImageError: cannot identify image file
```

### 5. Embedding Dimension Mismatch
```python
# Training used 512-dim, runtime uses different dimension
ValueError: X has 44 features, but SVC is expecting 512 features
```

## 📋 Step-by-Step Debugging Guide

### Step 1: Enable Detailed Logging

Add to `backend/app.py`:

```python
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flask_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
```

### Step 2: Add Error Handler to App

Add to `backend/app.py` in `create_app()`:

```python
@app.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {e}", exc_info=True)
    
    # Return JSON instead of HTML for HTTP errors
    return jsonify({
        'error': 'Internal server error',
        'message': str(e),
        'type': type(e).__name__
    }), 500
```

### Step 3: Validate Model Loading on Startup

Add to `backend/app.py` after `create_app()`:

```python
def validate_system():
    """Validate system components on startup"""
    logger.info("="*60)
    logger.info("SYSTEM VALIDATION")
    logger.info("="*60)
    
    # Check model files
    import os
    from config import config
    
    model_path = config.MODEL_PATH
    classifier_file = os.path.join(model_path, 'face_classifier_v1.pkl')
    classes_file = os.path.join(model_path, 'label_encoder_classes.npy')
    
    logger.info(f"Model path: {model_path}")
    logger.info(f"Classifier exists: {os.path.exists(classifier_file)}")
    logger.info(f"Classes exists: {os.path.exists(classes_file)}")
    
    # Check dependencies
    try:
        import torch
        logger.info(f"✅ PyTorch version: {torch.__version__}")
    except ImportError:
        logger.error("❌ PyTorch not installed")
        logger.error("Install with: pip install torch torchvision")
    
    try:
        import facenet_pytorch
        logger.info(f"✅ facenet-pytorch installed")
    except ImportError:
        logger.error("❌ facenet-pytorch not installed")
        logger.error("Install with: pip install facenet-pytorch")
    
    # Try to load model
    try:
        from recognizer.loader import model_loader
        success = model_loader.load_models()
        if success:
            logger.info("✅ Model loaded successfully")
            metadata = model_loader.get_metadata()
            if metadata:
                logger.info(f"   Embedding dim: {metadata.get('embedding_dim', 'unknown')}")
                logger.info(f"   Num classes: {metadata.get('num_classes', 'unknown')}")
                logger.info(f"   Threshold: {metadata.get('threshold', 'unknown')}")
        else:
            logger.error("❌ Model loading failed")
    except Exception as e:
        logger.error(f"❌ Model loading error: {e}")
        import traceback
        traceback.print_exc()
    
    # Check MTCNN/FaceNet
    try:
        from recognizer.embeddings_facenet import embedding_generator
        if embedding_generator and embedding_generator.is_available():
            logger.info("✅ FaceNet embedding generator available")
        else:
            logger.error("❌ FaceNet embedding generator not available")
    except Exception as e:
        logger.error(f"❌ FaceNet check failed: {e}")
    
    logger.info("="*60)

# Call validation after app creation
if __name__ == '__main__':
    app = create_app()
    validate_system()  # Add this line
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
```

### Step 4: Enhanced Attendance Endpoint

Update `backend/blueprints/attendance.py` recognize endpoint:

```python
@attendance_bp.route('/recognize', methods=['POST'])
@jwt_required()
@role_required('instructor')
def recognize_face():
    """Recognize face and record attendance with comprehensive error handling"""
    import traceback
    
    try:
        logger.info("="*60)
        logger.info("RECOGNITION REQUEST")
        logger.info("="*60)
        
        # Validate request
        if 'image' not in request.files and 'image' not in request.form:
            logger.error("No image provided in request")
            return jsonify({
                'status': 'error',
                'error': 'No image provided',
                'message': 'Please provide an image'
            }), 400
        
        session_id = request.form.get('session_id')
        if not session_id:
            logger.error("No session ID provided")
            return jsonify({
                'status': 'error',
                'error': 'Session ID required',
                'message': 'Please provide a session ID'
            }), 400
        
        logger.info(f"Session ID: {session_id}")
        
        # Validate session
        db = get_db()
        try:
            session = db.sessions.find_one({'_id': ObjectId(session_id)})
        except Exception as e:
            logger.error(f"Invalid session ID format: {e}")
            return jsonify({
                'status': 'error',
                'error': 'Invalid session ID format',
                'message': str(e)
            }), 400
        
        if not session:
            logger.error(f"Session not found: {session_id}")
            return jsonify({
                'status': 'error',
                'error': 'Session not found',
                'message': f'Session {session_id} does not exist'
            }), 404
        
        if session['status'] != 'active':
            logger.error(f"Session not active: {session['status']}")
            return jsonify({
                'status': 'error',
                'error': 'Session not active',
                'message': f'Session status is {session["status"]}'
            }), 400
        
        logger.info("✅ Session validated")
        
        # Get image data
        try:
            if 'image' in request.files:
                image_file = request.files['image']
                image_data = image_file.read()
                logger.info(f"Image from file: {len(image_data)} bytes")
            else:
                image_data = request.form.get('image')
                logger.info(f"Image from form data")
        except Exception as e:
            logger.error(f"Error reading image: {e}")
            return jsonify({
                'status': 'error',
                'error': 'Image read failed',
                'message': str(e)
            }), 400
        
        # Recognize face
        logger.info("Starting face recognition...")
        try:
            from recognizer.classifier import face_recognizer
            result = face_recognizer.recognize(image_data)
            logger.info(f"Recognition result: {result['status']}")
            
            if result['status'] == 'error':
                logger.error(f"Recognition error: {result.get('error')}")
                # Return 200 with error status (not 500)
                return jsonify(result), 200
            
            if result['status'] == 'no_face':
                logger.warning("No face detected")
                return jsonify(result), 200
            
            if result['status'] == 'unknown':
                logger.warning("Unknown face")
                return jsonify(result), 200
            
            if result['status'] == 'recognized':
                student_id = result['student_id']
                confidence = result['confidence']
                logger.info(f"Recognized: {student_id} (confidence: {confidence:.4f})")
                
                # Get student info
                student = db.students.find_one({'student_id': student_id})
                if not student:
                    logger.error(f"Student not in database: {student_id}")
                    return jsonify({
                        'status': 'unknown',
                        'message': f'Student {student_id} not found in database'
                    }), 200
                
                # Check duplicate
                today = date.today().isoformat()
                existing = db.attendance.find_one({
                    'student_id': student_id,
                    'session_id': session_id,
                    'date': today
                })
                
                if existing:
                    logger.info(f"Already marked: {student['name']}")
                    return jsonify({
                        'status': 'already_marked',
                        'message': f'{student["name"]} already marked present',
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
                db.sessions.update_one(
                    {'_id': ObjectId(session_id)},
                    {'$inc': {'attendance_count': 1}}
                )
                
                logger.info(f"✅ Attendance recorded: {student['name']}")
                
                return jsonify({
                    'status': 'recognized',
                    'student_id': student_id,
                    'student_name': student['name'],
                    'confidence': confidence,
                    'message': f'Attendance recorded for {student["name"]}'
                }), 200
            
            return jsonify(result), 200
            
        except ImportError as e:
            logger.error(f"Missing dependency: {e}")
            return jsonify({
                'status': 'error',
                'error': 'Missing dependencies',
                'message': 'Face recognition dependencies not installed. Install torch, torchvision, facenet-pytorch',
                'details': str(e)
            }), 500
            
        except RuntimeError as e:
            logger.error(f"Runtime error: {e}")
            return jsonify({
                'status': 'error',
                'error': 'Recognition system error',
                'message': str(e),
                'details': 'Check if model is trained and loaded correctly'
            }), 500
            
        except Exception as e:
            logger.error(f"Recognition exception: {e}")
            logger.error(traceback.format_exc())
            return jsonify({
                'status': 'error',
                'error': 'Recognition failed',
                'message': str(e),
                'type': type(e).__name__
            }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'error': 'Unexpected error',
            'message': str(e),
            'type': type(e).__name__
        }), 500
```

### Step 5: Test Model Loading Script

Create `backend/test_model_loading.py`:

```python
"""
Test script to verify model loading and recognition pipeline
Run this to diagnose issues before starting the server
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def test_dependencies():
    """Test if all dependencies are installed"""
    print("\n" + "="*60)
    print("TESTING DEPENDENCIES")
    print("="*60)
    
    deps = {
        'torch': 'PyTorch',
        'torchvision': 'TorchVision',
        'facenet_pytorch': 'FaceNet PyTorch',
        'PIL': 'Pillow',
        'cv2': 'OpenCV',
        'numpy': 'NumPy',
        'sklearn': 'Scikit-learn'
    }
    
    for module, name in deps.items():
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - NOT INSTALLED")
    
    print("="*60)

def test_model_files():
    """Test if model files exist"""
    print("\n" + "="*60)
    print("TESTING MODEL FILES")
    print("="*60)
    
    from config import config
    
    model_path = config.MODEL_PATH
    print(f"Model directory: {model_path}")
    print(f"Exists: {os.path.exists(model_path)}")
    
    files = {
        'face_classifier_v1.pkl': 'Main classifier',
        'label_encoder_classes.npy': 'Student IDs',
        'X.npy': 'Embeddings (optional)',
        'y.npy': 'Labels (optional)',
        'training_metadata.json': 'Metadata (optional)'
    }
    
    for filename, desc in files.items():
        filepath = os.path.join(model_path, filename)
        exists = os.path.exists(filepath)
        size = os.path.getsize(filepath) if exists else 0
        status = "✅" if exists else "❌"
        print(f"{status} {desc}: {filename} ({size} bytes)")
    
    print("="*60)

def test_model_loading():
    """Test model loading"""
    print("\n" + "="*60)
    print("TESTING MODEL LOADING")
    print("="*60)
    
    try:
        from recognizer.loader import model_loader
        
        success = model_loader.load_models()
        
        if success:
            print("✅ Model loaded successfully")
            
            metadata = model_loader.get_metadata()
            if metadata:
                print(f"   Embedding dimension: {metadata.get('embedding_dim')}")
                print(f"   Number of classes: {metadata.get('num_classes')}")
                print(f"   Confidence threshold: {metadata.get('threshold')}")
                print(f"   Classifier type: {metadata.get('classifier_type')}")
                print(f"   Students: {', '.join(metadata.get('classes', [])[:5])}...")
        else:
            print("❌ Model loading failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("="*60)

def test_facenet():
    """Test FaceNet initialization"""
    print("\n" + "="*60)
    print("TESTING FACENET")
    print("="*60)
    
    try:
        from recognizer.embeddings_facenet import embedding_generator
        
        if embedding_generator.is_available():
            print("✅ FaceNet available")
            
            # Test embedding generation
            import numpy as np
            test_img = np.random.randint(0, 255, (160, 160, 3), dtype=np.uint8)
            embedding = embedding_generator.generate_embedding(test_img)
            
            print(f"   Embedding shape: {embedding.shape}")
            print(f"   Embedding dimension: {embedding.shape[0]}")
            
            if embedding.shape[0] == 512:
                print("✅ Correct embedding dimension (512)")
            else:
                print(f"❌ Wrong embedding dimension: {embedding.shape[0]}, expected 512")
        else:
            print("❌ FaceNet not available")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("="*60)

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("FACE RECOGNITION SYSTEM DIAGNOSTICS")
    print("="*60)
    
    test_dependencies()
    test_model_files()
    test_model_loading()
    test_facenet()
    
    print("\n" + "="*60)
    print("DIAGNOSTICS COMPLETE")
    print("="*60)
    print("\nIf all tests pass, the system should work correctly.")
    print("If any tests fail, fix the issues before starting the server.\n")

if __name__ == '__main__':
    main()
```

## 🔧 Quick Fixes

### Fix 1: Install Missing Dependencies

```bash
cd backend
venv\Scripts\activate
pip install torch torchvision facenet-pytorch
```

### Fix 2: Restart Backend After Training

```bash
# Stop backend (Ctrl+C)
# Restart
python app.py
```

### Fix 3: Check Model Files

```bash
dir backend\models\Classifier
```

Should show:
- `face_classifier_v1.pkl`
- `label_encoder_classes.npy`

### Fix 4: Run Diagnostics

```bash
cd backend
python test_model_loading.py
```

### Fix 5: Check Backend Logs

Look for these in terminal:
```
✅ [Loader] Loaded classifier
✅ [Loader] Detected new model format
✅ [Loader] Embedding dim: 512
✅ FaceNet embedding generator available
```

## 📊 Expected vs Actual

### Expected Behavior
```
POST /api/attendance/recognize
→ Load image
→ Detect face with MTCNN
→ Extract 512-dim embedding with FaceNet
→ Classify with trained SVM
→ Return student_id + confidence
```

### Common Failures

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: torch` | PyTorch not installed | `pip install torch torchvision` |
| `Model not found` | Model not trained | Run `train_production_model.py` |
| `Embedding dimension mismatch` | Old model format | Retrain with new script |
| `MTCNN initialization failed` | First request issue | Restart backend |
| `No face detected` | Poor image quality | Use better lighting |

## 🎯 Verification Checklist

After implementing fixes:

- [ ] Dependencies installed (`pip list | grep torch`)
- [ ] Model files exist (`dir models\Classifier`)
- [ ] Diagnostics pass (`python test_model_loading.py`)
- [ ] Backend starts without errors
- [ ] Model loads on startup (check logs)
- [ ] Test endpoint returns 200 (not 500)
- [ ] Face recognition works in frontend

## 📝 Logging Best Practices

1. **Use structured logging**:
```python
logger.info(f"Processing image: size={len(data)} bytes")
logger.debug(f"Embedding shape: {embedding.shape}")
logger.error(f"Failed: {error}", exc_info=True)
```

2. **Log at key points**:
- Request received
- Image decoded
- Face detected
- Embedding generated
- Classification result
- Database operation

3. **Include context**:
```python
logger.info(f"Student {student_id} recognized with confidence {confidence:.4f}")
```

4. **Use appropriate levels**:
- `DEBUG`: Detailed diagnostic info
- `INFO`: General informational messages
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

## 🚀 Next Steps

1. Run diagnostics: `python test_model_loading.py`
2. Fix any failing tests
3. Restart backend with logging enabled
4. Test recognition endpoint
5. Check logs for detailed error messages
6. Fix issues based on log output

Your system should now provide detailed error messages instead of generic 500 errors!
