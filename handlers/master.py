import telebot
from telebot import types
from database import get_conn, seed_data


def register_master_handlers(bot):
    # 1. Команда /seed для наполнения базы
    @bot.message_handler(commands=['seed'])
    def handle_seed(message):
        result = seed_data()
        bot.reply_to(message, result)

    # 2. Кнопка "Регламенты и штрафы"
    @bot.message_handler(func=lambda message: message.text == "📜 Регламенты и штрафы")
    def show_regulations_menu(message):
        with get_conn() as conn:
            cur = conn.cursor()
            # Выбираем уникальные категории
            cur.execute("SELECT DISTINCT category FROM regulations ORDER BY category")
            categories = cur.fetchall()

        if not categories:
            bot.reply_to(
                message,
                "⚠️ В базе нет категорий регламентов!\n"
                "Запустите команду /seed."
            )
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

        # ИСПРАВЛЕНИЕ ЗДЕСЬ: берем row['category'], а не просто row
        for row in categories:
            cat_name = row['category']
            markup.add(types.KeyboardButton(f"📂 {cat_name}"))

        markup.add(types.KeyboardButton("🔙 Назад в меню мастера"))
        bot.send_message(message.chat.id, "Выберите категорию регламентов:", reply_markup=markup)

    # 3. Обработка выбора категории (кнопки вида "📂 Гигиена")
    @bot.message_handler(func=lambda message: message.text.startswith("📂 "))
    def show_regulations_category(message):
        # Убираем префикс "📂 "
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
            # item - это sqlite3.Row, обращаемся по имени колонки
            title = item['title']
            text = item['full_text']
            response_text += f"🔹 <b>{title}</b>\n{text}\n\n"

        bot.send_message(message.chat.id, response_text, parse_mode='HTML')

    # 4. Кнопка "Стерилизация и СанПиН" (Твоя подробная инструкция)
    @bot.message_handler(func=lambda message: message.text == "✨ Стерилизация и СанПиН")
    def handle_sterilization(message):
        text = (
            "🧼 <b>Инструкция по дезинфекции, ПСО и стерилизации инструментов</b>\n\n"
            "<b>1. Дезинфекция</b>\n"
            "• Подготовка: Раскройте ножницы и кусачки полностью.\n"
            "• Погружение: В УЗ-мойку с дезраствором.\n"
            "• Экспозиция: 5 минут.\n\n"
            "<b>2. ПСО (Предстерилизационная очистка)</b>\n"
            "• Промывание: Под проточной водой 5–7 минут.\n"
            "• Очистка фрез: Металлической щеточкой.\n\n"
            "<b>3. Сушка</b>\n"
            "• Просушивание: На чистой салфетке.\n"
            "• Важно: Влажные инструменты в сухожар ЗАПРЕЩЕНО.\n\n"
            "<b>4. Упаковка и документация</b>\n"
            "• Комплектация: По крафт-пакетам.\n"
            "• Маркировка: Дата, подпись, содержимое.\n"
            "• Журнал: Внесите данные (сухожар, инструменты, пакеты, параметры 200°C/30мин, подпись).\n\n"
            "<b>5. Стерилизация в сухожаре Beauty</b>\n"
            "• Закладка: Пакеты на полочки без наложения.\n"
            "• Контроль: Химические индикаторы в разные части камеры.\n"
            "• Режим: 200 °C на 30 минут.\n\n"
            "<b>6. Завершение</b>\n"
            "• Фиксация: Вклейте отработавшие индикаторы в журнал.\n"
            "• Охлаждение: Дайте инструментам остыть в пакетах.\n"
            "• Готово: Остывшие инструменты стерильны."
        )
        bot.send_message(message.chat.id, text, parse_mode='HTML')
