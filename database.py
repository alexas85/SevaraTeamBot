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
        # Таблица для инструкций (старая)
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

        # НОВАЯ ТАБЛИЦА для регламентов/штрафов
        cur.execute("""
            CREATE TABLE IF NOT EXISTS regulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,      -- Категория (например, "Дисциплина", "СанПиН")
                title TEXT NOT NULL,         -- Заголовок кнопки (кратко)
                full_text TEXT NOT NULL,     -- Полный текст строки из таблицы
                sort_order INTEGER DEFAULT 0  -- Порядок сортировки
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
