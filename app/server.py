import sys
import os
import hashlib
import html
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from app.detector import detect_payload
from app.database import log_attack

# ── App configuration ─────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-dev-key-do-not-use-in-prod")

FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))


def _sanitize(value: str) -> str:
    """Escape HTML entities to prevent log injection / XSS in outputs."""
    return html.escape(str(value))[:512]  # cap length to prevent log flooding


def _hash_password(plain: str) -> str:
    """One-way hash for any credential comparison — never store plain text."""
    return hashlib.sha256(plain.encode()).hexdigest()


# ── Routes ─────────────────────────────────────────────────────────────

@app.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.json or {}
    sanitized = {k: _sanitize(v) for k, v in data.items()}
    attack = detect_payload(sanitized)
    if attack:
        log_attack("admin", attack, request.remote_addr, sanitized)
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401


@app.route("/trap/login", methods=["POST"])
def trap_login():
    data = request.json or {}
    sanitized = {k: _sanitize(v) for k, v in data.items()}
    attack = detect_payload(sanitized)
    if attack:
        log_attack("trap", attack, request.remote_addr, sanitized)
    return jsonify({"status": "success", "message": "Welcome to the honeypot"}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


# ── Entry point ────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=FLASK_PORT)
