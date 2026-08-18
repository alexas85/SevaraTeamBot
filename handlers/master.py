import telebot
from telebot import types
from database import seed_data


def register_master_handlers(bot):
    @bot.message_handler(commands=['seed'])
    def handle_seed(message):
        try:
            count = seed_data()
            bot.reply_to(message, f"✅ Успешно! В базу добавлено {count} правил.")
        except Exception as e:
            bot.reply_to(message, f"❌ Ошибка при наполнении базы: {e}")

    @bot.message_handler(func=lambda message: message.text == "Регламенты и штрафы")
    def show_regulations_menu(message):
        from database import get_conn
        with get_conn() as conn:
            cur = conn.cursor()
            # Получаем уникальные категории
            cur.execute("SELECT DISTINCT category FROM regulations ORDER BY sort_order")
            categories = cur.fetchall()

        if not categories:
            bot.reply_to(
                message,
                "⚠️ В базе данных нет категорий регламентов!\n"
                "Запустите скрипт наполнения командой /seed в главном меню."
            )
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

        # ИСПРАВЛЕНИЕ: берем row, так как fetchall возвращает кортежи
        for row in categories:
            cat_name = row
            markup.add(types.KeyboardButton(f"📂 {cat_name}"))

        markup.add(types.KeyboardButton("🔙 Назад в меню мастера"))

        bot.send_message(
            message.chat.id,
            "Выберите категорию регламентов:",
            reply_markup=markup
        )

    @bot.message_handler(func=lambda message: message.text.startswith("📂 "))
    def show_regulations_category(message):
        category_name = message.text.replace("📂 ", "")
        from database import get_conn

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
            response_text += f"🔹 <b>{item['title']}</b>\n{item['full_text']}\n\n"

        bot.send_message(message.chat.id, response_text, parse_mode='HTML')

    @bot.message_handler(func=lambda message: message.text == "🔙 Назад в меню мастера")
    def go_back_to_master_menu(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("✨ Стерилизация и СанПиН"))
        markup.add(types.KeyboardButton("🧹 Чистота и оборудование"))
        markup.add(types.KeyboardButton("📜 Регламенты и штрафы"))
        markup.add(types.KeyboardButton("🔙 Назад в главное меню"))

        bot.send_message(message.chat.id, "Меню мастера студии Sevara:", reply_markup=markup)
