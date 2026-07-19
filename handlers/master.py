import telebot
from telebot import types

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

        # Пример простого пункта меню
        if text == "📖 Инструкции для мастера":
            bot.reply_to(message, "Здесь будут инструкции для мастера. Пока в разработке.")
            show_master_back_buttons(bot, message)
            return

def show_master_main_menu(bot: telebot.TeleBot, message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btns = [
        types.KeyboardButton("📖 Инструкции для мастера"),
    ]
    btns.append(types.KeyboardButton("🔙 Назад в меню мастера"))
    markup.add(*btns)
    bot.send_message(message.chat.id, "Меню мастера студии Sevara:", reply_markup=markup)

def show_master_back_buttons(bot: telebot.TeleBot, message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_back = types.KeyboardButton("🔙 Назад в меню мастера")
    markup.add(btn_back)
    bot.send_message(
        message.chat.id,
        "Нажмите «Назад», чтобы вернуться к выбору роли.",
        reply_markup=markup
    )
