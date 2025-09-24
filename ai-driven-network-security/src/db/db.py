"""
Lightweight SQLite helper to store alerts.
"""
import sqlite3
from datetime import datetime
import os

DB_PATH = os.environ.get("ALERT_DB_PATH", "data/processed/alerts.db")

def init_db(path=DB_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT,
        src TEXT,
        dst TEXT,
        proto TEXT,
        score REAL,
        metadata TEXT
    )"""
    )
    conn.commit()
    conn.close()

def insert_alert(src, dst, proto, score, metadata="", path=DB_PATH):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute(
        "INSERT INTO alerts (ts, src, dst, proto, score, metadata) VALUES (?, ?, ?, ?, ?, ?)",
        (datetime.utcnow().isoformat(), src, dst, proto, score, metadata),
    )
    conn.commit()
    conn.close()

def get_recent(limit=50, path=DB_PATH):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("SELECT id, ts, src, dst, proto, score, metadata FROM alerts ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    insert_alert("1.2.3.4", "5.6.7.8", "TCP", 0.123, '{"note":"example"}')
    print(get_recent())
