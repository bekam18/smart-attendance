"""
Minimal Flask app to test if the issue is in Flask itself
"""

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/test', methods=['POST'])
def test():
    data = request.get_json()
    return jsonify({'message': 'success', 'data': data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)