#!/usr/bin/env python3
"""Test analytics blueprint separately"""

from flask import Flask, Blueprint, jsonify
from flask_jwt_extended import JWTManager, jwt_required
from flask_cors import CORS

# Create a minimal test app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret'
app.config['JWT_SECRET_KEY'] = 'test-jwt-secret'

CORS(app)
jwt = JWTManager(app)

# Create test blueprint
test_bp = Blueprint('test', __name__)

@test_bp.route('/analytics/test', methods=['GET'])
def test_analytics():
    """Test analytics endpoint"""
    return jsonify({'message': 'Analytics endpoint working', 'data': []}), 200

@test_bp.route('/analytics/simple', methods=['GET'])
def simple_analytics():
    """Simple analytics endpoint"""
    return jsonify({'sections': [{'section': 'A', 'attendance': 85}]}), 200

# Register blueprint
app.register_blueprint(test_bp, url_prefix='/api/admin')

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    print("Test Analytics Server")
    print("Routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}")
    
    app.run(host='127.0.0.1', port=5001, debug=True)