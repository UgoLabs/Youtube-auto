import sqlite3
from typing import Optional

def init_db(db_name="faceless_agent.db"):
    """
    Connects to (or creates) an SQLite database and sets up tables if they don't exist.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS q_values (
            state TEXT,
            action TEXT,
            value REAL,
            PRIMARY KEY (state, action)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance_logs (
            video_id TEXT PRIMARY KEY,
            watch_time REAL,
            ctr REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def save_q_value(conn, state: str, action: str, value: float):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO q_values (state, action, value)
        VALUES (?, ?, ?)
    """, (state, action, value))
    conn.commit()

def get_q_value(conn, state: str, action: str) -> Optional[float]:
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM q_values WHERE state=? AND action=?", (state, action))
    row = cursor.fetchone()
    return row[0] if row else None

def save_performance(conn, video_id: str, watch_time: float, ctr: float):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO performance_logs (video_id, watch_time, ctr)
        VALUES (?, ?, ?)
    """, (video_id, watch_time, ctr))
    conn.commit()

def close_db(conn):
    conn.close()
