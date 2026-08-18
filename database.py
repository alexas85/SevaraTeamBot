import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "sevara.db"


def get_conn():
    """Возвращает соединение с row_factory=sqlite3.Row для удобного доступа по ключам."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # <--- ЭТО КРИТИЧЕСКИ ВАЖНО! Без этого будет ошибка Row object
    return conn


def init_db():
    """Создает таблицы, если их нет."""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS regulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                full_text TEXT NOT NULL,
                sort_order INTEGER DEFAULT 0
            )
        """)
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


def seed_data():
    """
    Наполняет базу данными.
    ВАЖНО: Эта функция проверяет, пуста ли таблица, прежде чем что-то удалять.
    Если таблица не пуста, она ничего не делает (чтобы не потерять данные).
    """
    with get_conn() as conn:
        cur = conn.cursor()

        # Проверяем, есть ли уже данные
        cur.execute("SELECT count(*) FROM regulations")
        count = cur.fetchone()[0]

        if count > 0:
            return f"База уже наполнена ({count} записей). Пропускаем seed."

        # Если пусто - добавляем тестовые данные
        test_data = [
            ("Гигиена и Санитария", "Обработка рук",
             "Мастер обязан обрабатывать руки антисептиком перед каждым клиентом."),
            ("Гигиена и Санитария", "Стерилизация инструментов",
             "Все инструменты проходят трехэтапную обработку: дезинфекция, ПСО, стерилизация."),
            ("Внешний вид", "Форма одежды", "Ношение фирменной формы обязательно. Волосы убраны."),
            ("Рабочее место", "Уборка", "Текущая уборка проводится после каждого клиента. Генеральная — раз в неделю."),
            ("Рабочее место", "Хранение материалов", "Расходные материалы хранятся в закрытых шкафах."),
            ("Техника безопасности", "Электрооборудование", "Не использовать приборы с поврежденной изоляцией."),
            ("Документация", "Журнал стерилизации", "Запись в журнале делается после каждой стерилизации.")
        ]

        cur.executemany(
            "INSERT INTO regulations (category, title, full_text, sort_order) VALUES (?, ?, ?, ?)",
            [(cat, title, text, idx) for idx, (cat, title, text) in enumerate(test_data)]
        )
        conn.commit()
        return f"Успешно добавлено {len(test_data)} правил."


def get_instruction(role: str, key: str):
    """Возвращает строку инструкции по роли и ключу или None."""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM instructions WHERE role = ? AND key = ?",
            (role, key)
        )
        return cur.fetchone()


def set_instruction_content(role: str, key: str, text_content: str = None,
                             description: str = None, photo_file_id: str = None,
                             video_file_id: str = None):
    """Создает или обновляет запись инструкции (upsert)."""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO instructions (role, key, text_content, description, photo_file_id, video_file_id)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(role, key) DO UPDATE SET
                text_content  = excluded.text_content,
                description   = excluded.description,
                photo_file_id = excluded.photo_file_id,
                video_file_id = excluded.video_file_id
        """, (role, key, text_content, description, photo_file_id, video_file_id))
        conn.commit()
