import sqlite3
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "sevara.db"


def get_conn():
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
    """Наполняет базу тестовыми данными для регламентов"""
    with get_conn() as conn:
        cur = conn.cursor()

        # Сначала очищаем таблицу, чтобы не дублировать данные при каждом /seed
        cur.execute("DELETE FROM regulations")

        test_data = [
            ("Гигиена и Санитария", "Обработка рук",
             "Мастер обязан обрабатывать руки антисептиком перед каждым клиентом..."),
            ("Гигиена и Санитария", "Стерилизация инструментов",
             "Все инструменты проходят трехэтапную обработку: дезинфекция, предстерилизационная очистка, стерилизация в автоклаве."),
            ("Внешний вид", "Форма одежды", "Ношение фирменной формы обязательно. Волосы убраны, маникюр аккуратный."),
            ("Клиентский сервис", "Встреча клиента",
             "Приветствие должно быть дружелюбным, предложение воды/чая обязательно."),
            ("Клиентский сервис", "Конфликты",
             "При возникновении конфликта необходимо пригласить старшего мастера. Самостоятельное решение запрещено."),
            ("Техника безопасности", "Электрооборудование",
             "Не использовать приборы с поврежденной изоляцией. Розетки должны быть сухими."),
            ("Техника безопасности", "Пожарная безопасность",
             "Знать расположение огнетушителя и плана эвакуации. Не загромождать проходы."),
            ("Рабочее место", "Уборка", "Текущая уборка проводится после каждого клиента. Генеральная — раз в неделю."),
            ("Рабочее место", "Хранение материалов",
             "Расходные материалы хранятся в закрытых шкафах, отдельно от мусора."),
            ("Документация", "Журнал стерилизации",
             "Запись в журнале делается после каждой стерилизации с указанием времени и ФИО ответственного.")
        ]

        cur.executemany(
            "INSERT INTO regulations (category, title, full_text, sort_order) VALUES (?, ?, ?, ?)",
            [(cat, title, text, idx) for idx, (cat, title, text) in enumerate(test_data)]
        )
        conn.commit()

        return len(test_data)


# Заглушка, чтобы main.py мог импортировать эту функцию без ошибок,
# даже если мы не используем её напрямую в этом файле.
def check_and_seed_data():
    init_db()
    count = seed_data()
    return f"База инициализирована. Добавлено правил: {count}"
