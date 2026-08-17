# handlers/admin.py
import telebot
from telebot import types
from database import get_instruction
from config import STATE_MAIN, STATE_ROLE_ADMIN


def register_admin_handlers(bot: telebot.TeleBot, user_states: dict):
    def ensure_state_main(chat_id):
        if chat_id not in user_states:
            user_states[chat_id] = STATE_MAIN

    @bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == STATE_ROLE_ADMIN)
    def handle_admin_menu(message):
        text = message.text

        if text == "🔙 Назад в админ‑меню":
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

        mapping_admin_view = {
            "🔑 Открытие и закрытие салона": ("admin", "opening_closing"),
            "📊 Работа в Yclients и Fitmost": ("admin", "yclients_fitmost"),
            "💵 Кассовая дисциплина и отчёты": ("admin", "cash_reports"),
            "📣 Скрипты общения и Продажи": ("admin", "scripts_sales"),
        }
        pair = mapping_admin_view.get(text)
        if pair:
            role, key = pair
            row = get_instruction(role, key)
            if row:
                if row.get("text_content"):
                    bot.send_message(message.chat.id, row["text_content"])
                if row.get("description"):
                    bot.send_message(message.chat.id, f"📝 Описание: {row['description']}")
                if row.get("photo_file_id"):
                    bot.send_photo(message.chat.id, photo=row["photo_file_id"])
                if row.get("video_file_id"):
                    bot.send_video(message.chat.id, video=row["video_file_id"])
            else:
                bot.send_message(message.chat.id, "Пока нет материалов по этому разделу.")
            show_admin_back_buttons(bot, message)
            return


def show_admin_main_menu(bot: telebot.TeleBot, message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btns = [
        types.KeyboardButton("🔑 Открытие и закрытие салона"),
        types.KeyboardButton("📊 Работа в Yclients и Fitmost"),
        types.KeyboardButton("💵 Кассовая дисциплина и отчёты"),
        types.KeyboardButton("📣 Скрипты общения и Продажи"),
    ]
    markup.add(*btns)
    bot.send_message(message.chat.id, "Панель администратора студии Sevara:", reply_markup=markup)


def show_admin_back_buttons(bot: telebot.TeleBot, message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_back = types.KeyboardButton("🔙 Назад в админ‑меню")
    markup.add(btn_back)
    bot.send_message(
        message.chat.id,
        "Выберите другой раздел или нажмите «Назад», чтобы вернуться к выбору роли.",
        reply_markup=markup
    )
