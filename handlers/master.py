import telebot
from telebot import types
from database import seed_data, get_conn


def register_master_handlers(bot):
    # --- 1. Команда /seed ---
    @bot.message_handler(commands=['seed'])
    def handle_seed(message):
        try:
            count = seed_data()
            bot.reply_to(message, f"✅ Успешно! В базу добавлено {count} правил.")
        except Exception as e:
            bot.reply_to(message, f"❌ Ошибка при наполнении базы: {e}")

    # --- 2. Кнопка "Регламенты и штрафы" (Сложный список категорий) ---
    @bot.message_handler(func=lambda message: message.text == "📜 Регламенты и штрафы")
    def show_regulations_menu(message):
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT category FROM regulations ORDER BY sort_order")
            categories = cur.fetchall()

        if not categories:
            bot.reply_to(
                message,
                "⚠️ В базе данных нет категорий регламентов!\n"
                "Запустите команду /seed."
            )
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for row in categories:
            cat_name = row
            markup.add(types.KeyboardButton(f"📂 {cat_name}"))

        markup.add(types.KeyboardButton("🔙 Назад в меню мастера"))
        bot.send_message(message.chat.id, "Выберите категорию регламентов:", reply_markup=markup)

    # --- 3. Обработка выбора категории (кнопки вида "📂 Гигиена") ---
    @bot.message_handler(func=lambda message: message.text.startswith("📂 "))
    def show_regulations_category(message):
        category_name = message.text.replace("📂 ", "")

        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT title, full_text FROM regulations WHERE category = ? ORDER BY sort_order",
                        (category_name,))
            items = cur.fetchall()

        if not items:
            bot.reply_to(message, "В этой категории пока нет правил.")
            return

        response_text = f"📜 Категория: {category_name}\n\n"
        for item in items:
            # Используем .get() для безопасной работы со словарем, если row_factory изменится
            title = item.get('title', 'Без названия')
            text = item.get('full_text', 'Нет текста')
            response_text += f"🔹 <b>{title}</b>\n{text}\n\n"

        bot.send_message(message.chat.id, response_text, parse_mode='HTML')

    # --- 4. Кнопка "Стерилизация и СанПиН" ---
    @bot.message_handler(func=lambda message: message.text == "✨ Стерилизация и СанПиН")
    def handle_sterilization(message):
        text = (
            "🧼 <b>Стерилизация и СанПиН в студии Sevara:</b>\n\n"
            "1. <b>Инструменты:</b> Все металлические инструменты проходят 3 этапа: дезинфекция -> ПСО -> стерилизация в автоклаве.\n"
            "2. <b>Расходники:</b> Одноразовые (перчатки, маски, салфетки) утилизируются сразу после клиента.\n"
            "3. <b>Поверхности:</b> Дезинфекция кресла, столиков и ручек проводится после каждого клиента.\n"
            "4. <b>Журнал:</b> Обязательно фиксировать время стерилизации и ФИО ответственного в журнале."
        )
        bot.send_message(message.chat.id, text, parse_mode='HTML')

    # --- 5. Кнопка "Чистота и оборудование" ---
    @bot.message_handler(func=lambda message: message.text == "🧹 Чистота и оборудование")
    def handle_cleanliness(message):
        text = (
            "🧹 <b>Чистота и оборудование в студии Sevara:</b>\n\n"
            "1. <b>Уборка:</b> Текущая уборка — после каждого клиента. Генеральная — 1 раз в неделю.\n"
            "2. <b>Оборудование:</b> Проверять исправность ламп, фенов и аппаратов перед началом смены.\n"
            "3. <b>Хранение:</b> Чистые расходники хранятся в закрытых шкафах. Грязное белье — в отдельном контейнере.\n"
            "4. <b>Мусор:</b> Вынос мусора — в конце каждой смены."
        )
        bot.send_message(message.chat.id, text, parse_mode='HTML')

    # --- 6. Кнопка "Назад в меню мастера" ---
    @bot.message_handler(func=lambda message: message.text == "🔙 Назад в меню мастера")
    def go_back_to_master_menu(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("✨ Стерилизация и СанПиН"))
        markup.add(types.KeyboardButton("🧹 Чистота и оборудование"))
        markup.add(types.KeyboardButton("📜 Регламенты и штрафы"))
        markup.add(types.KeyboardButton("🔙 Назад в главное меню"))

        bot.send_message(message.chat.id, "Меню мастера студии Sevara:", reply_markup=markup)

    # --- 7. Кнопка "Назад в главное меню" ---
    @bot.message_handler(func=lambda message: message.text == "🔙 Назад в главное меню")
    def back_to_start(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("👷 Я мастер"))
        bot.send_message(message.chat.id, "Выберите роль:", reply_markup=markup)
