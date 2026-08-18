import sqlite3
from pathlib import Path
import os

# Определяем путь к базе: сначала пробуем текущую директорию, потом корень проекта
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "sevara.db"


def get_conn():
    # Создаем директорию, если её вдруг нет (на некоторых хостингах это критично)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
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
        cur.execute("""
            CREATE TABLE IF NOT EXISTS regulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                full_text TEXT NOT NULL,
                sort_order INTEGER DEFAULT 0
            )
        """)
        conn.commit()


def seed_data():
    """Принудительное наполнение базы данными (можно вызывать из чата)"""
    with get_conn() as conn:
        cur = conn.cursor()

        # Очищаем таблицу перед вставкой, чтобы не было дублей
        cur.execute("DELETE FROM regulations")

        REGULATIONS_DATA = [
            {"category": "Качество работы", "title": "Переделка работы другим мастером",
             "full_text": "📋 Нарушение: Переделка работы другим мастером.\n💰 Санкция: 100% стоимости услуги + 10% на расходники.",
             "sort_order": 1},
            {"category": "Качество работы", "title": "Самостоятельная переделка брака",
             "full_text": "📋 Нарушение: Самостоятельная переделка брака без согласования.\n💰 Санкция: Процент не начисляется, удержание себестоимости материалов.",
             "sort_order": 2},
            {"category": "Дисциплина и имущество", "title": "Вынос материалов/инструментов",
             "full_text": "📋 Нарушение: Вынос материалов или инструментов студии без разрешения.\n💰 Санкция: Штраф 5 000 ₽, удержание стоимости вещей.",
             "sort_order": 3},
            {"category": "Дисциплина и имущество", "title": "Опоздание на смену (от 15 мин)",
             "full_text": "📋 Нарушение: Опоздание на смену более чем на 15 минут.\n💰 Санкция: Штраф 500 ₽.",
             "sort_order": 4},
            {"category": "Дисциплина и имущество", "title": "Невыход на смену без предупреждения",
             "full_text": "📋 Нарушение: Невыход на смену без предупреждения руководителя.\n💰 Санкция: Штраф 2 000 ₽ + возмещение стоимости записей.",
             "sort_order": 5},
            {"category": "СанПиН и безопасность", "title": "Нарушение правил стерилизации",
             "full_text": "📋 Нарушение: Нарушение правил стерилизации инструментов.\n💰 Санкция: Штраф 1 000 ₽.",
             "sort_order": 6},
            {"category": "Дисциплина и имущество", "title": "Оставленное грязным рабочее место",
             "full_text": "📋 Нарушение: Рабочее место оставлено грязным после смены.\n💰 Санкция: Штраф 500 ₽.",
             "sort_order": 7},
            {"category": "Финансы и касса", "title": "Непробитый чек / Сокрытие оплаты",
             "full_text": "📋 Нарушение: Непробитый чек или сокрытие оплаты услуги.\n💰 Санкция: Штраф 100% от суммы услуги.",
             "sort_order": 8},
            {"category": "Финансы и касса", "title": "Порча имущества по небрежности",
             "full_text": "📋 Нарушение: Порча имущества студии по небрежности.\n💰 Санкция: Удержание 100% стоимости ремонта.",
             "sort_order": 9},
            {"category": "Работа с клиентами", "title": "Жалоба на грубость",
             "full_text": "📋 Нарушение: Жалоба клиента на грубость или некорректное поведение.\n💰 Санкция: Списание 50% стоимости услуги в пользу клиента.",
             "sort_order": 10}
        ]

        for item in REGULATIONS_DATA:
            cur.execute("""
                INSERT INTO regulations (category, title, full_text, sort_order)
                VALUES (?, ?, ?, ?)
            """, (item["category"], item["title"], item["full_text"], item["sort_order"]))

        conn.commit()
        return len(REGULATIONS_DATA)


def get_instruction(role: str, key: str):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM instructions WHERE role=? AND key=?", (role, key))
        row = cur.fetchone()
        return dict(row) if row else None


def set_instruction_content(role: str, key: str, text_content: str = None, description: str = None):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO instructions (role, key, text_content, description)
            VALUES (?, ?, ?, ?)
        """, (role, key, text_content, description))
        conn.commit()


def set_photo_for_category(role: str, key: str, file_id: str):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO instructions (role, key, photo_file_id)
            VALUES (?, ?, ?)
        """, (role, key, file_id))
        conn.commit()


def set_video_for_category(role: str, key: str, file_id: str):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO instructions (role, key, video_file_id)
            VALUES (?, ?, ?)
        """, (role, key, file_id))
        conn.commit()
