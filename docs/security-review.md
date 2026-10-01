# SentinelTrap-Web — Security Review

> **Classification:** Public Portfolio  
> **Reviewed:** 2026-10-01  
> **Standard:** OWASP Top 10, CWE/SANS Top 25

---

## 1. Secret Management & Environment Isolation

| Item | Status | Notes |
|------|--------|-------|
| Hardcoded secrets | ✅ NONE | All secrets removed from source code |
| `SECRET_KEY` | ✅ ENV | Loaded via `os.getenv("SECRET_KEY")` with dotenv |
| `DB_PATH` | ✅ ENV | Loaded via `os.getenv("DB_PATH")` with dotenv |
| `.env` committed | ✅ BLOCKED | Listed in `.gitignore` |
| `.env.example` | ✅ PROVIDED | Safe placeholder values only — no real keys |

**Policy:** Zero hardcoded secrets. All sensitive configuration is injected at runtime through environment variables using `python-dotenv`. The `.env` file is excluded from version control via `.gitignore`. A `.env.example` template is provided for onboarding.

---

## 2. Password & Credential Security

| Item | Status | Notes |
|------|--------|-------|
| Plain-text storage | ✅ NONE | No passwords stored anywhere |
| Credential comparison | ✅ HASHED | `hashlib.sha256` used for any credential check |
| Honeypot auth bypass | ✅ INTENTIONAL | Honeypot endpoints always return error/success to trap attackers — no real auth |

**Policy:** The honeypot intentionally accepts all login attempts (trap endpoint) to lure and log attackers. No real user credentials exist. If credential comparison is ever needed, `hashlib.sha256` is used — plain-text comparison is forbidden.

---

## 3. Injection Protection

### 3a. Input Sanitization

All incoming request data passes through `_sanitize()` in `server.py` before storage or analysis:

```python
def _sanitize(value: str) -> str:
    return html.escape(str(value))[:512]
```

- **HTML entity encoding** prevents XSS in any downstream rendering
- **Length cap (512 chars)** prevents log flooding / DoS via oversized payloads

### 3b. Detection Engine (`app/detector.py`)

The detection engine uses compiled regex patterns against sanitized input:

| Attack Type | Patterns Covered |
|-------------|-----------------|
| **SQL Injection** | `OR`, `AND`, `SELECT`, `UNION`, `DROP`, `INSERT`, `UPDATE`, `EXEC`, quote chars, `1=1` |
| **XSS** | `<script>`, `javascript:`, `onerror=`, `onload=`, `alert()`, `document.cookie`, `eval()` |
| **Scanner / Recon** | `sqlmap`, `nikto`, `nmap`, `masscan`, `nessus`, `dirbuster`, `metasploit`, path traversal patterns |
| **Path Traversal** | `../`, `etc/passwd`, `cmd.exe`, `powershell` |

### 3c. Database Safety

All database writes use **parameterized queries** (SQLite `?` placeholders):

```python
conn.execute(
    "INSERT INTO attacks (endpoint, attack_type, ip, payload) VALUES (?,?,?,?)",
    (endpoint, attack_type, ip, str(payload)),
)
```

This prevents second-order SQL injection via stored payloads.

### 3d. Dashboard Output Sanitization

All data displayed in the Streamlit dashboard is HTML-escaped before rendering:

```python
df["Payload"] = df["Payload"].apply(lambda x: html.escape(str(x))[:200])
df["IP"] = df["IP"].apply(lambda x: html.escape(str(x)))
```

---

## 4. Honeypot Architecture Security

### Isolation Principles

```
Internet (Attacker)
        │
        ▼
 Flask Honeypot (0.0.0.0:5000)
   /admin/login  → logs & returns 401
   /trap/login   → logs & returns 200 (lure)
        │
        ▼
  Detection Engine (in-process, no network)
        │
        ▼
  SQLite Database (local file, no network exposure)
        │
        ▼
  Streamlit Dashboard (127.0.0.1:8501 — localhost only)
```

### Attacker Containment Measures

| Risk | Mitigation |
|------|-----------|
| Attacker pivoting to internal systems | Flask binds to `0.0.0.0:5000` only; Dashboard on `127.0.0.1:8501` (not externally reachable) |
| Payload execution | All payloads treated as **data strings only** — never executed or eval'd |
| Log injection | All input HTML-escaped and length-capped before storage |
| Database exposure | SQLite file excluded from git and not served over any network interface |
| Information leakage via error pages | Flask runs in production mode (`debug=False`); generic error messages only |

### Deployment Recommendation

For production/research environments, deploy the Flask honeypot in an **isolated network segment** (VM, container, or DMZ) with:
- Outbound traffic blocked (prevent attacker C2 callbacks)
- Inbound limited to honeypot port only
- Streamlit dashboard on a separate internal-only interface

---

## 5. Open Issues & Future Work

| Priority | Item |
|----------|------|
| Medium | Add rate limiting (`flask-limiter`) to prevent log flooding |
| Medium | Add GeoIP resolution for attacker IP enrichment |
| Low | Implement SIEM export (CEF/JSON log format) |
| Low | Add alerting webhook (Slack/Discord) on new attack detection |

---

*This document is auto-generated for portfolio and educational purposes. SentinelTrap-Web is a research honeypot — do not deploy on production systems without additional hardening.*
