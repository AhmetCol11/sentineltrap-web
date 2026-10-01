import sqlite3
import os
from contextlib import closing
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── DB path from env, fallback to <project_root>/app/attacks.db ───────
_default_db = str(Path(__file__).resolve().parent / "attacks.db")
DB_PATH = os.getenv("DB_PATH", _default_db)


def init_db() -> None:
    """Ensure the attacks table exists."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS attacks (
                id          INTEGER  PRIMARY KEY AUTOINCREMENT,
                endpoint    TEXT     NOT NULL,
                attack_type TEXT     NOT NULL,
                ip          TEXT,
                payload     TEXT,
                timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def log_attack(endpoint: str, attack_type: str, ip: str, payload) -> None:
    """Insert a sanitized attack record into the database."""
    init_db()
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            "INSERT INTO attacks (endpoint, attack_type, ip, payload) VALUES (?,?,?,?)",
            (endpoint, attack_type, ip, str(payload)),
        )
        conn.commit()
