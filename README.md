# SentinelTrap-Web 🛡️

> **A professional Web Honeypot & Cyber Security Analysis Panel** — Built for CV-level portfolio demonstration.

![SentinelTrap Dashboard](dashboard/dashboard.png)

---

## Overview
SentinelTrap-Web exposes fake admin and trap login endpoints (Flask), detects common attack payloads (SQLi, XSS, scanning probes) and logs them to a SQLite database. A modern Streamlit SOC dashboard visualizes attacks in real-time with metrics and charts.

## Architecture
![Architecture Diagram](sentineltrap_architecture_1790868026213.jpg)

## Features
- 🎣 Fake `admin/login` and `trap/login` honeypot endpoints
- 🔍 Payload detection: SQL Injection, XSS, Path Traversal, Scanner fingerprints
- 🗄️ SQLite attack logging (endpoint, attack type, IP, payload, timestamp)
- 📊 Streamlit SOC dashboard — metrics, attack table, bar chart
- 🐳 Dockerized deployment via `docker-compose`
- ⚡ Single-click local startup via `baslat.bat`

## Quick Start (Local)

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Install dependencies
.\venv\Scripts\pip.exe install -r requirements.txt

# 3. Launch all services (Windows)
baslat.bat
```

- **Honeypot API:** http://localhost:5000
- **SOC Dashboard:** http://localhost:8501

## Quick Start (Docker)

```bash
docker-compose up --build
```

## Project Structure

```
sentineltrap-web/
├── app/
│   ├── server.py      # Flask honeypot endpoints
│   ├── detector.py    # SQLi / XSS / Scanner detection engine
│   └── database.py    # SQLite logging layer
├── dashboard/
│   └── app.py         # Streamlit SOC dashboard
├── baslat.bat         # One-click Windows launcher
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## License
MIT
