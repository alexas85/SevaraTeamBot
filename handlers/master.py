import telebot
from telebot import types
from database import get_instruction

def show_master_main_menu(bot: telebot.TeleBot, message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btns = [
        types.KeyboardButton("✨ Стерилизация и СанПиН"),
        types.KeyboardButton("💨 Чистота и оборудование"),
    ]
    btns.append(types.KeyboardButton("🔙 Назад в меню мастера"))
    markup.add(*btns)
    bot.send_message(message.chat.id, "Меню мастера студии Sevara:", reply_markup=markup)


def register_master_handlers(bot: telebot.TeleBot, user_states: dict):
    def ensure_state_main(chat_id):
        if chat_id not in user_states:
            user_states[chat_id] = "main"

    @bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == "Я мастер")
    def handle_master_menu(message):
        text = message.text

        if text == "🔙 Назад в меню мастера":
            ensure_state_main(message.chat.id)
            user_states[message.chat.id] = "main"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn_master = types.KeyboardButton("Я мастер")
            btn_admin = types.KeyboardButton("Я администратор")
            markup.add(btn_master, btn_admin)
            bot.send_message(
                message.chat.id,
                "Ты вернулся к выбору роли:",
                reply_markup=markup
            )
            return

        # --- ИНСТРУКЦИЯ ПО СТЕРИЛИЗАЦИИ (вставлена прямо сюда) ---
        if text == "✨ Стерилизация и СанПиН":
            instruction_text = (
                "🧼 Инструкция по дезинфекции, ПСО и стерилизации инструментов\n\n"
                "1. Дезинфекция\n"
                "   Подготовка: Раскройте ножницы и кусачки полностью. Фрезы разложите отдельно в специальный отсек (лоток).\n"
                "   Погружение: Поместите инструменты в ультразвуковую (УЗ) мойку с дезинфицирующим раствором.\n"
                "   Экспозиция: Выдержите инструменты в УЗ-мойке ровно 5 минут.\n\n"
                "2. Предстерилизационная очистка (ПСО)\n"
                "   Промывание: Промойте инструменты под проточной водой в течение 5–7 минут.\n"
                "   Очистка фрез: Тщательно очистите фрезы металлической щеточкой для удаления кожного жира (себума) и остатков опила.\n"
                "   Примечание: Металлическую щетку используйте только для фрез, соприкасавшихся с кожей.\n\n"
                "3. Сушка\n"
                "   Просушивание: Выложите инструменты на чистую салфетку. Дождитесь их полного высыхания (влажные инструменты закладывать в сухожар запрещено).\n\n"
                "4. Упаковка и ведение документации\n"
                "   Комплектация: Разложите полностью сухие инструменты по крафт-пакетам.\n"
                "   Маркировка: Заполните информацию на крафт-пакетах (дата, подпись, содержимое).\n"
                "   Заполнение журнала: Внесите данные в журнал контроля работы стерилизаторов:\n"
                "     • Название сухожара: Свами Beauty (СБ)\n"
                "     • Наименование и точное количество инструментов (ножницы, фрезы, кусачки и т.д.).\n"
                "     • Количество задействованных крафт-пакетов.\n"
                "     • Параметры стерилизации: 200 °C / 30 минут.\n"
                "     • Подпись ответственного лица.\n\n"
                "5. Стерилизация в сухожаре Beauty\n"
                "   Закладка: Поместите крафт-пакеты в сухожаровой шкаф Beauty на специальные полочки без наложения друг на друга.\n"
                "   Контроль: Используйте химические индикаторы (режимные, на 200 °C / 30 мин). Закладывайте их в разные части камеры (вперед и назад) для контроля равномерного распределения тепла.\n"
                "   Режим: Запустите цикл стерилизации на 200 °C на 30 минут.\n\n"
                "6. Завершение процесса\n"
                "   Фиксация контроля: После окончания цикла вклейте отработавшие индикаторы в журнал стерилизации.\n"
                "   Охлаждение: Дайте инструментам полностью остыть внутри пакетов. Остывшие стерильные инструменты готовы к работе."
            )
            bot.send_message(message.chat.id, instruction_text, parse_mode="Markdown")
            show_master_back_buttons(bot, message)
            return
        # ---------------------------------------------------------

        if text == "💨 Чистота и оборудование":
            row = get_instruction("master", "cleanliness")
            if row and (row["text_content"] or row["description"] or row["photo_file_id"] or row["video_file_id"]):
                if row["text_content"]:
                    bot.send_message(message.chat.id, row["text_content"])
                if row["description"]:
                    bot.send_message(message.chat.id, f"📝 Описание: {row['description']}")
                if row["photo_file_id"]:
                    bot.send_photo(message.chat.id, photo=row["photo_file_id"])
                if row["video_file_id"]:
                    bot.send_video(message.chat.id, video=row["video_file_id"])
            else:
                bot.send_message(message.chat.id, "Пока нет материалов по этой теме.")
            show_master_back_buttons(bot, message)
            return


def show_master_back_buttons(bot: telebot.TeleBot, message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_back = types.KeyboardButton("🔙 Назад в меню мастера")
    markup.add(btn_back)
    bot.send_message(
        message.chat.id,
        "Нажмите «Назад», чтобы вернуться в меню мастера.",
        reply_markup=markup
    )
