import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask, request, jsonify
from app.detector import detect_payload
from app.database import log_attack

app = Flask(__name__)

@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json or {}
    attack = detect_payload(data)
    if attack:
        log_attack('admin', attack, request.remote_addr, data)
    return jsonify({'status':'error','message':'Invalid credentials'}), 401

@app.route('/trap/login', methods=['POST'])
def trap_login():
    data = request.json or {}
    attack = detect_payload(data)
    if attack:
        log_attack('trap', attack, request.remote_addr, data)
    return jsonify({'status':'success','message':'Welcome to the honeypot'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
