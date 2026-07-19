import telebot
from telebot import types
from database import get_instruction

# Выносим функцию на верхний уровень — теперь её можно импортировать
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

        if text == "✨ Стерилизация и СанПиН":
            row = get_instruction("master", "sterilization")
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
