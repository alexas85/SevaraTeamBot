# handlers/master.py
import telebot
from telebot import types
from database import get_instruction, get_conn
from config import STATE_ROLE_MASTER, STATE_MAIN

import logging
logger = logging.getLogger('SevaraTeamBot')


def show_master_main_menu(bot: telebot.TeleBot, message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btns = [
        types.KeyboardButton("✨ Стерилизация и СанПиН"),
        types.KeyboardButton("💨 Чистота и оборудование"),
        types.KeyboardButton("📜 Регламенты и штрафы")
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

        if text == "📜 Регламенты и штрафы":
            show_regulations_categories(bot, message)
            return

            # --- ДОБАВЛЕННЫЙ БЛОК: Обработка выбора категории из кнопок ---
        if text.startswith("📂 "):
            category_name = text.replace("📂 ", "")
            # Вызываем функцию показа правил внутри категории
            show_regulations_by_category(bot, message, category_name)
            return

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

        if text == "✨ Стерилизация и СанПиН":
            row = get_instruction("master", "sterilization_sanpin")
            if row and row.get("text_content"):
                bot.send_message(message.chat.id, row["text_content"], parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "Инструкция по стерилизации временно недоступна.")
            show_master_back_buttons(bot, message)
            return

        if text == "💨 Чистота и оборудование":
            row = get_instruction("master", "cleanliness")
            has_content = False
            if row:
                if row.get("text_content"):
                    bot.send_message(message.chat.id, row["text_content"])
                    has_content = True
                if row.get("description"):
                    bot.send_message(message.chat.id, f"📝 Описание: {row['description']}")
                    has_content = True
                if row.get("photo_file_id"):
                    bot.send_photo(message.chat.id, photo=row["photo_file_id"])
                    has_content = True
                if row.get("video_file_id"):
                    bot.send_video(message.chat.id, video=row["video_file_id"])
                    has_content = True

            if not has_content:
                bot.send_message(message.chat.id, "Пока нет материалов по этой теме.")
            show_master_back_buttons(bot, message)
            return

        if text == "📜 Регламенты и штрафы":
            show_regulations_categories(bot, message)
            return

    @bot.callback_query_handler(func=lambda call: call.data.startswith("reg_detail_"))
    def callback_handler(call):
        handle_regulation_callback(bot, call)


def show_regulations_categories(bot: telebot.TeleBot, message):
    """Показывает кнопки с категориями штрафов"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

    try:
        with get_conn() as conn:
            cur = conn.cursor()
            # Используем DISTINCT, чтобы получить уникальные категории
            cur.execute("SELECT DISTINCT category FROM regulations ORDER BY category")
            categories = cur.fetchall()

        if not categories:
            # ВАЖНО: Это сообщение поможет тебе понять, что база пуста
            bot.send_message(
                message.chat.id,
                "⚠️ Внимание: В базе данных нет категорий регламентов!\n"
                "Запустите скрипт наполнения seed_regulations.py на сервере.",
                reply_markup=markup
            )
            return

        for row in categories:
            cat_name = row  # row — это кортеж, берём первый элемент
            markup.add(types.KeyboardButton(f"📂 {cat_name}"))

        markup.add(types.KeyboardButton("🔙 Назад в меню мастера"))

        bot.send_message(
            message.chat.id,
            "Выберите категорию правил, чтобы узнать детали:",
            reply_markup=markup
        )
    except Exception as e:
        logger.error(f"Ошибка при получении категорий регламентов: {e}")
        bot.send_message(
            message.chat.id,
            f"Произошла ошибка при загрузке категорий: {str(e)}"
        )
def show_regulations_by_category(bot: telebot.TeleBot, message, category_name):
    """Показывает список правил внутри категории"""
    clean_category = category_name.replace("📂 ", "")
    markup = types.InlineKeyboardMarkup(row_width=1)

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, title FROM regulations WHERE category = ? ORDER BY sort_order", (clean_category,))
        rows = cur.fetchall()

        for reg_id, title in rows:
            btn = types.InlineKeyboardButton(title, callback_data=f"reg_detail_{reg_id}")
            markup.add(btn)

    bot.send_message(
        message.chat.id,
        f"Правила категории: <b>{clean_category}</b>\nВыберите пункт для подробностей:",
        reply_markup=markup,
        parse_mode="HTML"
    )


def handle_regulation_callback(bot: telebot.TeleBot, call):
    """Обрабатывает нажатие на конкретное правило"""
    if call.data.startswith("reg_detail_"):
        try:
            reg_id = int(call.data.split("_")[-1])

            with get_conn() as conn:
                cur = conn.cursor()
                cur.execute("SELECT full_text FROM regulations WHERE id = ?", (reg_id,))
                row = cur.fetchone()

                if row:
                    text_content = row[0]

                    bot.answer_callback_query(call.id)
                    bot.send_message(call.message.chat.id, text_content, parse_mode="HTML")
                else:
                    bot.answer_callback_query(call.id, "Правило не найдено", show_alert=True)
        except Exception as e:
            print(f"Error in regulation callback: {e}")
            bot.answer_callback_query(call.id, "Произошла ошибка при загрузке правила", show_alert=True)


def show_master_back_buttons(bot: telebot.TeleBot, message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_back = types.KeyboardButton("🔙 Назад в меню мастера")
    markup.add(btn_back)

    bot.send_message(
        message.chat.id,
        "Нажмите «Назад», чтобы вернуться в меню мастера.",
        reply_markup=markup
    )
