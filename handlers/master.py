import telebot
from telebot import types
from database import get_instruction
# Если ты ещё не создал config.py — пока оставь импорты из main, но лучше вынести константы (см. ниже)
from main import STATE_ROLE_MASTER, STATE_MAIN


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
            user_states[chat_id] = STATE_MAIN

    @bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == STATE_ROLE_MASTER)
    def handle_master_menu(message):
        text = message.text

        # Кнопка «Назад»
        if text == "🔙 Назад в меню мастера":
            ensure_state_main(message.chat.id)
            user_states[message.chat.id] = STATE_MAIN
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

        # Стерилизация — теперь из БД
        if text == "✨ Стерилизация и СанПиН":
            row = get_instruction("master", "sterilization_sanpin")
            if row and row["text_content"]:
                bot.send_message(message.chat.id, row["text_content"], parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "Инструкция по стерилизации временно недоступна.")
            show_master_back_buttons(bot, message)
            return

        # Чистота и оборудование
        if text == "💨 Чистота и оборудование":
            row = get_instruction("master", "cleanliness")
            # Отправляем всё, что есть: текст, описание, фото, видео
            has_content = False
            if row:
                if row["text_content"]:
                    bot.send_message(message.chat.id, row["text_content"])
                    has_content = True
                if row["description"]:
                    bot.send_message(message.chat.id, f"📝 Описание: {row['description']}")
                    has_content = True
                if row["photo_file_id"]:
                    bot.send_photo(message.chat.id, photo=row["photo_file_id"])
                    has_content = True
                if row["video_file_id"]:
                    bot.send_video(message.chat.id, video=row["video_file_id"])
                    has_content = True

            if not has_content:
                bot.send_message(message.chat.id, "Пока нет материалов по этой теме.")
            show_master_back_buttons(bot, message)
            return


def show_master_back_buttons(bot: telebot.TeleBot, message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_back = types.KeyboardButton("🔙 Назад в меню мастера")
    markup.add(btn_back)
    # Можно не слать новое сообщение, а просто вернуть клавиатуру, если хочешь меньше спама.
    # Но пока оставляем как было.
    bot.send_message(
        message.chat.id,
        "Нажмите «Назад», чтобы вернуться в меню мастера.",
        reply_markup=markup
    )
