import telebot
from telebot import types
from database import get_instruction

def register_master_handlers(bot: telebot.TeleBot, user_states: dict):

    @bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == "Я мастер")
    def handle_master_menu(message):
        text = message.text

        # Кнопка «В главное меню» — отдельный приоритет
        if text == "🔙 В главное меню":
            # Не делаем ничего здесь: главный хендлер в bot.py уже обработает это
            return

        if text == "↩️ Назад к разделам мастера":
            show_master_main_menu(bot, message)
            return

        mapping = {
            "✨ Стерилизация и СанПиН": "sterilization",
            "💨 Чистота и оборудование": "cleanliness",
            "👗 Внешний вид и форма": "appearance",
            "☕️ Сервис и Quiet Luxury": "service",
        }
        key = mapping.get(text)
        if not key:
            return

        row = get_instruction("master", key)
        if row:
            bot.send_message(message.chat.id, row["text_content"])
            if row["photo_file_id"]:
                bot.send_photo(message.chat.id, photo=row["photo_file_id"])
            if row["video_file_id"]:
                bot.send_video(message.chat.id, video=row["video_file_id"])

        show_back_buttons(bot, message)


def show_master_main_menu(bot: telebot.TeleBot, message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btns = [
        types.KeyboardButton("✨ Стерилизация и СанПиН"),
        types.KeyboardButton("💨 Чистота и оборудование"),
        types.KeyboardButton("👗 Внешний вид и форма"),
        types.KeyboardButton("☕️ Сервис и Quiet Luxury"),
    ]
    # Кнопка возврата в самое начало
    btns.append(types.KeyboardButton("🔙 В главное меню"))
    markup.add(*btns)
    bot.send_message(message.chat.id, "Меню мастера:", reply_markup=markup)


def show_back_buttons(bot: telebot.TeleBot, message):
    """Кнопки: «Назад к разделам» и «В главное меню»"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_back = types.KeyboardButton("↩️ Назад к разделам мастера")
    btn_main = types.KeyboardButton("🔙 В главное меню")
    markup.add(btn_back, btn_main)
    bot.send_message(
        message.chat.id,
        "Выберите другой раздел или вернитесь в главное меню.",
        reply_markup=markup
    )
