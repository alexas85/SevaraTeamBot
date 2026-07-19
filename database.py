import sqlite3
from pathlib import Path

DB_PATH = Path("sevara.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        # Добавлено поле description
        cur.execute("""
            CREATE TABLE IF NOT EXISTS instructions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                key TEXT NOT NULL,
                text_content TEXT,
                description TEXT,
                photo_file_id TEXT,
                video_file_id TEXT,
                UNIQUE(role, key)
            )
        """)
        conn.commit()

def get_instruction(role: str, key: str):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM instructions WHERE role=? AND key=?",
            (role, key)
        )
        row = cur.fetchone()
        return dict(row) if row else None

def set_instruction_content(role: str, key: str, text_content: str = None, description: str = None):
    """Обновляет текст и/или описание инструкции."""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT OR REPLACE INTO instructions (role, key, text_content, description)
            VALUES (?, ?, ?, ?)
            """,
            (role, key, text_content, description)
        )
        conn.commit()

def set_photo_for_category(role: str, key: str, file_id: str):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT OR REPLACE INTO instructions (role, key, photo_file_id)
            VALUES (?, ?, ?)
            """,
            (role, key, file_id)
        )
        conn.commit()

def set_video_for_category(role: str, key: str, file_id: str):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT OR REPLACE INTO instructions (role, key, video_file_id)
            VALUES (?, ?, ?)
            """,
            (role, key, file_id)
        )
        conn.commit()
