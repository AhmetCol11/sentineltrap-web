import sqlite3
from contextlib import closing
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'attacks.db')

def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS attacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint TEXT NOT NULL,
            attack_type TEXT NOT NULL,
            ip TEXT,
            payload TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()

def log_attack(endpoint, attack_type, ip, payload):
    init_db()
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute('INSERT INTO attacks (endpoint, attack_type, ip, payload) VALUES (?,?,?,?)',
                     (endpoint, attack_type, ip, str(payload)))
        conn.commit()
