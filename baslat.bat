@echo off

echo Servisler baslatiliyor...
start "Flask Honeypot" cmd /k ".\venv\Scripts\python.exe -m app.server"
timeout /t 2 >nul
start "Streamlit SOC Dashboard" cmd /k ".\venv\Scripts\python.exe -m streamlit run dashboard\app.py --server.port 8501"
timeout /t 3 >nul
start http://localhost:8501
echo Tamamlandi! Pencereleri kapatmayin.
