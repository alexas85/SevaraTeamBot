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

    # --- 2. Кнопка "Регламенты и штрафы" ---
    @bot.message_handler(func=lambda message: message.text == "📜 Регламенты и штрафы")
    def show_regulations_menu(message):
        with get_conn() as conn:
            cur = conn.cursor()
            # Получаем только названия категорий (column 0)
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

        # ИСПРАВЛЕНИЕ ОШИБКИ: берем row (текст), а не весь объект row
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
            # item - это sqlite3.Row, к нему можно обращаться по имени колонки
            title = item['title']
            text = item['full_text']
            response_text += f"🔹 <b>{title}</b>\n{text}\n\n"

        bot.send_message(message.chat.id, response_text, parse_mode='HTML')

    # --- 4. Кнопка "Стерилизация и СанПиН" (Твоя подробная инструкция) ---
    @bot.message_handler(func=lambda message: message.text == "✨ Стерилизация и СанПиН")
    def handle_sterilization(message):
        # Вставляем твою подробную инструкцию сюда, чтобы она работала гарантированно
        text = (
            "🧼 <b>Инструкция по дезинфекции, ПСО и стерилизации инструментов</b>\n\n"
            "<b>1. Дезинфекция</b>\n"
            "• Подготовка: Раскройте ножницы и кусачки полностью. Фрезы разложите отдельно.\n"
            "• Погружение: Поместите инструменты в УЗ-мойку с дезраствором.\n"
            "• Экспозиция: Выдержите ровно 5 минут.\n\n"

            "<b>2. Предстерилизационная очистка (ПСО)</b>\n"
            "• Промывание: Под проточной водой 5–7 минут.\n"
            "• Очистка фрез: Металлической щеточкой удалите себум и опил.\n"
            "• Важно: Щетку используйте только для фрез, соприкасавшихся с кожей.\n\n"

            "<b>3. Сушка</b>\n"
            "• Просушивание: Выложите на чистую салфетку.\n"
            "• Критично: Влажные инструменты в сухожар закладывать ЗАПРЕЩЕНО.\n\n"

            "<b>4. Упаковка и документация</b>\n"
            "• Комплектация: Разложите сухие инструменты по крафт-пакетам.\n"
            "• Маркировка: Дата, подпись, содержимое на пакете.\n"
            "• Журнал: Внесите данные в журнал контроля:\n"
            "   - Сухожар: Свами Beauty (СБ)\n"
            "   - Инструменты: точное количество и список\n"
            "   - Пакеты: количество\n"
            "   - Параметры: 200 °C / 30 минут\n"
            "   - Подпись ответственного.\n\n"

            "<b>5. Стерилизация в сухожаре Beauty</b>\n"
            "• Закладка: Пакеты на полочки без наложения друг на друга.\n"
            "• Контроль: Химические индикаторы (200°C/30мин) в разные части камеры.\n"
            "• Режим: 200 °C на 30 минут.\n\n"

            "<b>6. Завершение процесса</b>\n"
            "• Фиксация: Вклейте отработавшие индикаторы в журнал.\n"
            "• Охлаждение: Дайте инструментам полностью остыть в пакетах.\n"
            "• Готово: Остывшие инструменты стерильны и готовы к работе."
        )
        bot.send_message(message.chat.id, text, parse_mode='HTML')

    # --- 5. Кнопка "Чистота и оборудование" ---
    @bot.message_handler(func=lambda message: message.text == "🧹 Чистота и оборудование")
    def handle_cleanliness(message):
        text = (
            "🧹 <b>Чистота и оборудование в студии Sevara:</b>\n\n"
            "1. <b>Уборка:</b> Текущая — после каждого клиента. Генеральная — 1 раз в неделю.\n"
            "2. <b>Оборудование:</b> Проверять исправность ламп, фенов и аппаратов перед сменой.\n"
            "3. <b>Хранение:</b> Чистые расходники — в закрытых шкафах. Грязное белье — в отдельном контейнере.\n"
            "4. <b>Мусор:</b> Вынос мусора — в конце каждой смены."
        )
        bot.send_message(message.chat.id, text, parse_mode='HTML')

    # --- 6. Кнопки навигации ---
    @bot.message_handler(func=lambda message: message.text == "🔙 Назад в меню мастера")
    def go_back_to_master_menu(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("✨ Стерилизация и СанПиН"))
        markup.add(types.KeyboardButton("🧹 Чистота и оборудование"))
        markup.add(types.KeyboardButton("📜 Регламенты и штрафы"))
        markup.add(types.KeyboardButton("🔙 Назад в главное меню"))
        bot.send_message(message.chat.id, "Меню мастера студии Sevara:", reply_markup=markup)

    @bot.message_handler(func=lambda message: message.text == "🔙 Назад в главное меню")
    def back_to_start(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("👷 Я мастер"))
        bot.send_message(message.chat.id, "Выберите роль:", reply_markup=markup)
