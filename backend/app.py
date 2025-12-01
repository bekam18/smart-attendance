from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

from config import config
from db.mongo import init_db
from blueprints.auth import auth_bp
from blueprints.admin import admin_bp
from blueprints.students import students_bp
from blueprints.attendance import attendance_bp
from blueprints.debug import debug_bp
from blueprints.instructor import instructor_bp

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = config.JWT_ACCESS_TOKEN_EXPIRES
    app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
    
    # Enable detailed error logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
    
    # CORS - Allow frontend to access API with automatic OPTIONS handling
    # automatic_options=True ensures Flask-CORS handles OPTIONS requests
    # before they reach route handlers, preventing JWT validation on preflight
    CORS(
        app, 
        resources={
            r"/api/*": {
                "origins": config.CORS_ORIGINS,
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True
            }
        },
        automatic_options=True  # Critical: Handle OPTIONS before routes
    )
    
    # JWT
    jwt = JWTManager(app)
    
    # Add error handlers for better debugging
    @app.errorhandler(Exception)
    def handle_error(e):
        app.logger.error(f"Unhandled exception: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'type': type(e).__name__
        }), 500
    
    # Database
    init_db()
    
    # Create upload folder
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(config.MODEL_PATH, exist_ok=True)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(students_bp, url_prefix='/api/students')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(instructor_bp, url_prefix='/api/instructor')
    app.register_blueprint(debug_bp, url_prefix='/api/debug')
    
    # Health check
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'service': 'SmartAttendance API'})
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Load model on startup
    print("\n" + "="*60)
    print("LOADING FACE RECOGNITION MODEL")
    print("="*60)
    try:
        from recognizer.loader import model_loader
        success = model_loader.load_models()
        if success:
            print("✅ Model loaded successfully")
            metadata = model_loader.get_metadata()
            if metadata:
                print(f"   Students: {metadata.get('num_classes', 0)}")
                print(f"   Threshold: {metadata.get('threshold', 0):.4f}")
        else:
            print("❌ Model loading failed - recognition will not work")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        import traceback
        traceback.print_exc()
    print("="*60 + "\n")
    
    print(f"🚀 SmartAttendance API running on http://{config.HOST}:{config.PORT}")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
