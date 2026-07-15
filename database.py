import sqlite3
from pathlib import Path

DB_PATH = Path("sevara.db")

def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        # Таблица инструкций (текст + file_id медиа)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS instructions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,              -- 'master' или 'admin'
                category_key TEXT NOT NULL,      -- уникальный ключ категории
                title TEXT NOT NULL,            -- заголовок кнопки
                text_content TEXT,              -- текст инструкции
                photo_file_id TEXT,             -- file_id фото
                video_file_id TEXT              -- file_id видео
            )
        """)
        # Уникальность по роли + категория
        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_role_category
            ON instructions(role, category_key)
        """)

        # Заполняем начальные данные (если пусто)
        cur.execute("SELECT count(*) FROM instructions")
        if cur.fetchone()[0] == 0:
            initial_data = [
                # Мастер
                ("master", "sterilization", "✨ Стерилизация и СанПиН",
                 "Регламент дезинфекции инструментов:\n1. Промывка под проточной водой.\n2. Замачивание в дезрастворе.\n3. Ополаскивание.\n4. Сушка.\n5. Упаковка в крафт-пакет с маркировкой даты и времени.\n\nВАЖНО: Вскрытие пакета происходит ТОЛЬКО при клиенте!",
                 None, None),

                ("master", "cleanliness", "💨 Чистота и оборудование",
                 "1. Вытяжка 4BLANC: регулировка света и мощности кнопками на корпусе.\n2. Пылесос Deerma DX700: HEPA-фильтры чистить ТОЛЬКО сухим методом (вытряхивание). НИКАКОЙ воды!\n3. Аппараты Strong 210/793: включать только с установленной фрезой. В конце дня обязательно выключать из розетки.",
                 None, None),

                ("master", "appearance", "👗 Внешний вид и форма",
                 "Стандарты студии Sevara:\n- Костюм: бежево-кофейный джоггер.\n- Обувь: чистая, закрытая.\n- Волосы: аккуратно собраны.\n- Парфюм: отсутствует или едва уловимый аромат. Защита от аллергии у клиентов на ресницах — приоритет!",
                 None, None),

                ("master", "service", "☕️ Сервис и Quiet Luxury",
                 "Правила общения:\n- Если клиент закрыл глаза — соблюдаем тишину.\n- Угощения: предлагайте чай/кофе из меню Choc Cafe ненавязчиво.\n- SPA-массаж рук: используйте одноразовую перчатку поверх маски/парафина.",
                 None, None),

                # Администратор
                ("admin", "opening_closing", "🔑 Открытие и закрытие салона",
                 "Чек-лист:\nОткрытие:\n- Включить свет/вывеску.\n- Включить фоновую музыку (только лаундж, никакого радио!).\n- Проверить чистоту.\n- Сварить свежий кофе.\n\nЗакрытие:\n- Выключить все приборы из розеток.\n- Закрыть окна.\n- Запереть дверь.",
                 None, None),

                ("admin", "yclients_fitmost", "📊 Работа в Yclients и Fitmost",
                 "Как правильно вести расписание:\n- Строго блокировать график Алины (или других мастеров на период отпуска), чтобы избежать двойных записей в Fitmost.\n\nАналитика:\n- Указывайте «Источник записи» точно: если клиент пришёл из Instagram, пишем Instagram, даже если общаемся в WhatsApp!",
                 None, None),

                ("admin", "cash_reports", "💵 Кассовая дисциплина и отчеты",
                 "Вечерний отчёт:\n- Сверка наличности.\n- Сверка терминала эквайринга.\n- Внесение данных в шаблон вечернего отчёта.",
                 None, None),

                ("admin", "scripts_sales", "📣 Скрипты общения и Продажи",
                 "Готовые шаблоны:\n- Скрипт перезаписи: на кассе закрывать клиента на следующий визит (цель — 50% перезаписи).\n- Бокс за отзыв: предлагать подарки из деревянного бокса за честный отзыв на 2ГИС.\n- VIP-время: продажа ранних записей на 8:00 к Жанне с доплатой +1000 ₽.",
                 None, None),
            ]
            cur.executemany("""
                INSERT INTO instructions(role, category_key, title, text_content, photo_file_id, video_file_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, initial_data)
        conn.commit()

def get_instruction(role: str, category_key: str):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM instructions WHERE role=? AND category_key=?",
            (role, category_key)
        )
        return cur.fetchone()

def update_instruction_text(role: str, category_key: str, text: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE instructions SET text_content=? WHERE role=? AND category_key=?",
            (text, role, category_key)
        )
        conn.commit()

def set_photo_for_category(role: str, category_key: str, file_id: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE instructions SET photo_file_id=? WHERE role=? AND category_key=?",
            (file_id, role, category_key)
        )
        conn.commit()

def set_video_for_category(role: str, category_key: str, file_id: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE instructions SET video_file_id=? WHERE role=? AND category_key=?",
            (file_id, role, category_key)
        )
        conn.commit()
