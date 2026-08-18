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
        count = cur.fetchone()

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
