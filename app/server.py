import sys
import os
import hashlib
import html
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from app.detector import detect_payload
from app.database import log_attack

# ── App configuration ─────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-dev-key-do-not-use-in-prod")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))

# ── Fake Corporate Login Page HTML ────────────────────────────────────
LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Acme Corp — Secure Portal</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet"/>
  <style>
    body {
      background: #0d1117;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'Segoe UI', sans-serif;
    }
    .login-card {
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 12px;
      padding: 2.5rem 2rem;
      width: 100%;
      max-width: 420px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.6);
    }
    .brand-logo {
      font-size: 1.8rem;
      font-weight: 700;
      color: #58a6ff;
      letter-spacing: -1px;
    }
    .brand-sub {
      color: #8b949e;
      font-size: 0.85rem;
      margin-bottom: 1.8rem;
    }
    .form-control {
      background: #0d1117;
      border: 1px solid #30363d;
      color: #c9d1d9;
      border-radius: 6px;
    }
    .form-control:focus {
      background: #0d1117;
      border-color: #58a6ff;
      color: #c9d1d9;
      box-shadow: 0 0 0 3px rgba(88,166,255,0.15);
    }
    .form-label { color: #8b949e; font-size: 0.85rem; }
    .btn-login {
      background: #238636;
      border: none;
      border-radius: 6px;
      color: #fff;
      width: 100%;
      padding: 0.6rem;
      font-weight: 600;
      transition: background 0.2s;
    }
    .btn-login:hover { background: #2ea043; color: #fff; }
    .alert-danger {
      background: #3d1f1f;
      border: 1px solid #f85149;
      color: #f85149;
      border-radius: 6px;
      font-size: 0.875rem;
    }
    .divider { border-color: #30363d; margin: 1.5rem 0; }
    .footer-text { color: #484f58; font-size: 0.75rem; text-align: center; margin-top: 1.2rem; }
    .lock-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
    input:-webkit-autofill {
      -webkit-box-shadow: 0 0 0 30px #0d1117 inset !important;
      -webkit-text-fill-color: #c9d1d9 !important;
    }
  </style>
</head>
<body>
<div class="login-card">
  <div class="text-center">
    <div class="lock-icon">🔐</div>
    <div class="brand-logo">Acme Corp</div>
    <div class="brand-sub">Enterprise Secure Portal · v4.2.1</div>
  </div>
  {% if error %}
  <div class="alert alert-danger" role="alert">
    ⚠️ {{ error }}
  </div>
  {% endif %}
  <form method="POST" action="/login">
    <div class="mb-3">
      <label for="username" class="form-label">Corporate Username</label>
      <input type="text" class="form-control" id="username" name="username"
             placeholder="domain\\username" autocomplete="off" required/>
    </div>
    <div class="mb-3">
      <label for="password" class="form-label">Password</label>
      <input type="password" class="form-control" id="password" name="password"
             placeholder="••••••••" autocomplete="off" required/>
    </div>
    <button type="submit" class="btn btn-login mt-1">Sign In</button>
  </form>
  <hr class="divider"/>
  <p class="footer-text">
    Unauthorized access is prohibited and monitored.<br/>
    &copy; 2024 Acme Corporation. All rights reserved.
  </p>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""


# ── Helpers ───────────────────────────────────────────────────────────

def _sanitize(value: str) -> str:
    """Escape HTML entities and cap length to prevent log injection."""
    return html.escape(str(value))[:512]


def _hash_password(plain: str) -> str:
    """One-way hash — never store plain text."""
    return hashlib.sha256(plain.encode()).hexdigest()


def _get_ip() -> str:
    return request.headers.get("X-Forwarded-For", request.remote_addr)


# ── Routes ─────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("login"))


@app.route("/admin", methods=["GET"])
def admin():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = _sanitize(request.form.get("username", ""))
        password = _sanitize(request.form.get("password", ""))
        payload = {"username": username, "password": password}
        attack = detect_payload(payload)
        if attack:
            log_attack("login_form", attack, _get_ip(), payload)
        else:
            # Log all login attempts even without known attack signature
            log_attack("login_form", "BruteForce", _get_ip(), payload)
        error = "Invalid credentials. Please try again."
    return render_template_string(LOGIN_PAGE, error=error)


@app.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.json or {}
    sanitized = {k: _sanitize(v) for k, v in data.items()}
    attack = detect_payload(sanitized)
    if attack:
        log_attack("admin_api", attack, _get_ip(), sanitized)
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401


@app.route("/trap/login", methods=["POST"])
def trap_login():
    data = request.json or {}
    sanitized = {k: _sanitize(v) for k, v in data.items()}
    attack = detect_payload(sanitized)
    if attack:
        log_attack("trap_api", attack, _get_ip(), sanitized)
    return jsonify({"status": "success", "message": "Welcome to the honeypot"}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


# ── Catch-all: log scanner/recon probes ──────────────────────────────

@app.errorhandler(404)
def catch_scanners(e):
    path = _sanitize(request.path)
    log_attack(
        f"recon:{path}",
        "Scanner",
        _get_ip(),
        {"path": path, "method": request.method, "ua": _sanitize(request.headers.get("User-Agent", ""))},
    )
    return redirect(url_for("login"))


# ── Entry point ────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=FLASK_PORT)
