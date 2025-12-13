from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
import logging

from config import Config as config
# from db.mongo import init_db  # Replaced with MySQL
from db.mysql import init_db
from blueprints.auth import auth_bp
from blueprints.admin import admin_bp
from blueprints.students import students_bp
from blueprints.attendance import attendance_bp
from blueprints.debug import debug_bp
from blueprints.instructor import instructor_bp

# Import security middleware
try:
    from middleware.working_security import working_security_check, working_audit_log
    SECURITY_AVAILABLE = True
    print("✅ Security middleware loaded successfully")
except ImportError as e:
    SECURITY_AVAILABLE = False
    print(f"⚠️  Security middleware not available: {e}")

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = config.JWT_ACCESS_TOKEN_EXPIRES
    app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
    
    # Enable detailed error logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    app.logger.setLevel(logging.INFO)
    
    # Security logging
    security_logger = logging.getLogger('security')
    security_handler = logging.FileHandler('logs/security.log')
    security_handler.setFormatter(logging.Formatter(
        '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
    ))
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.WARNING)
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
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
    
    # Security headers and middleware
    @app.after_request
    def after_request(response):
        # Add comprehensive security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        return response
    
    # Apply security middleware to all API routes
    if SECURITY_AVAILABLE:
        @app.before_request
        def security_check():
            # Apply security validation to all API routes
            if request.path.startswith('/api/'):
                return working_security_check(lambda: None)()
        
        print("✅ Security middleware applied to all API routes")
    
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
    
    # Request logging (enabled for debugging)
    @app.before_request
    def log_request():
        print(f"🌐 REQUEST: {request.method} {request.path}")
        if request.is_json:
            print(f"   JSON: {request.get_json()}")
        import sys
        sys.stdout.flush()
    
    # Register blueprints
    print("🔧 Registering blueprints...")
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    print("✅ Auth blueprint registered")
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    print("✅ Admin blueprint registered")
    app.register_blueprint(students_bp, url_prefix='/api/students')
    print("✅ Students blueprint registered")
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    print("✅ Attendance blueprint registered")
    app.register_blueprint(instructor_bp, url_prefix='/api/instructor')
    print("✅ Instructor blueprint registered")
    app.register_blueprint(debug_bp, url_prefix='/api/debug')
    print("✅ Debug blueprint registered")
    
    # Debug: Print all registered routes
    print(f"\n📋 Total routes registered: {len(list(app.url_map.iter_rules()))}")
    analytics_routes = [rule for rule in app.url_map.iter_rules() if 'analytics' in rule.rule]
    print(f"📊 Analytics routes: {len(analytics_routes)}")
    for route in analytics_routes:
        print(f"   {route.rule}")
    print()
    
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
    
    # Load model on startup (temporarily disabled)
    # print("\n" + "="*60)
    # print("LOADING FACE RECOGNITION MODEL")
    # print("="*60)
    # try:
    #     from recognizer.loader import model_loader
    #     success = model_loader.load_models()
    #     if success:
    #         print("✅ Model loaded successfully")
    #         metadata = model_loader.get_metadata()
    #         if metadata:
    #             print(f"   Students: {metadata.get('num_classes', 0)}")
    #             print(f"   Threshold: {metadata.get('threshold', 0):.4f}")
    #     else:
    #         print("❌ Model loading failed - recognition will not work")
    # except Exception as e:
    #     print(f"❌ Error loading model: {e}")
    #     import traceback
    #     traceback.print_exc()
    # print("="*60 + "\n")
    
    print(f"🚀 SmartAttendance API running on http://{config.HOST}:{config.PORT}")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
