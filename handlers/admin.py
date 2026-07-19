import telebot
from telebot import types
from database import get_instruction, set_photo_for_category, set_video_for_category, set_instruction_content

# upload_state: user_id -> {"role": str, "key": str, "waiting_for": "description"|"media"}
upload_state = {}

def register_admin_handlers(bot: telebot.TeleBot, user_states: dict):
    def ensure_state_main(chat_id):
        if chat_id not in user_states:
            user_states[chat_id] = "main"

    @bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == "Я администратор")
    def handle_admin_menu(message):
        text = message.text

        # Кнопка «Назад в админ‑меню» — возвращает к выбору роли
        if text == "🔙 Назад в админ‑меню":
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

        # Загрузка медиа
        if text == "📤 Загрузить медиа для инструкций":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            btns = [
                types.KeyboardButton("✨ Стерилизация и СанПиН (мастер)"),
                types.KeyboardButton("💨 Чистота и оборудование (мастер)"),
                types.KeyboardButton("🔑 Открытие и закрытие салона (админ)"),
                types.KeyboardButton("📊 Работа в Yclients и Fitmost (админ)"),
            ]
            # ДОБАВЛЕНА кнопка «Назад» прямо в это меню
            btns.append(types.KeyboardButton("🔙 Назад в админ‑меню"))
            markup.add(*btns)
            bot.reply_to(message, "Выберите категорию, куда загрузить фото/видео:", reply_markup=markup)
            return

        mapping_upload = {
            "✨ Стерилизация и СанПиН (мастер)": ("master", "sterilization"),
            "💨 Чистота и оборудование (мастер)": ("master", "cleanliness"),
            "🔑 Открытие и закрытие салона (админ)": ("admin", "opening_closing"),
            "📊 Работа в Yclients и Fitmost (админ)": ("admin", "yclients_fitmost"),
        }
        pair = mapping_upload.get(text)
        if pair:
            role, key = pair
            # Теперь мы сначала ждём описание
            upload_state[message.chat.id] = {"role": role, "key": key, "waiting_for": "description"}
            bot.reply_to(
                message,
                f"Отлично! Сначала напишите короткое описание для категории «{text}»:\n(потом отправьте фото или видео)"
            )
            return

        # Просмотр разделов админа
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
                if row["text_content"]:
                    bot.send_message(message.chat.id, row["text_content"])
                if row["description"]:
                    bot.send_message(message.chat.id, f"📝 Описание: {row['description']}")
                if row["photo_file_id"]:
                    bot.send_photo(message.chat.id, photo=row["photo_file_id"])
                if row["video_file_id"]:
                    bot.send_video(message.chat.id, video=row["video_file_id"])
            show_admin_back_buttons(bot, message)
            return

    # Обработка сообщений при загрузке (описание или медиа)
    @bot.message_handler(func=lambda msg: msg.chat.id in upload_state)
    def handle_upload_flow(message):
        user_id = message.chat.id
        state = upload_state.get(user_id)
        if not state:
            return

        if state["waiting_for"] == "description":
            # Сохраняем описание
            set_instruction_content(
                state["role"],
                state["key"],
                description=message.text
            )
            # Меняем ожидание на медиа
            state["waiting_for"] = "media"
            bot.reply_to(
                message,
                "Описание сохранено! Теперь отправьте фото или видео для этой категории."
            )
            return

        elif state["waiting_for"] == "media":
            file_id = None
            if message.photo:
                file_id = message.photo[-1].file_id
                set_photo_for_category(state["role"], state["key"], file_id)
                bot.reply_to(message, "Фото сохранено!")
            elif message.video:
                file_id = message.video.file_id
                set_video_for_category(state["role"], state["key"], file_id)
                bot.reply_to(message, "Видео сохранено!")

            # Завершаем загрузку
            upload_state.pop(user_id, None)
            show_admin_main_menu(bot, message)
            return

    @bot.message_handler(content_types=["photo", "video"], func=lambda msg: msg.chat.id in upload_state and upload_state[msg.chat.id]["waiting_for"] == "media")
    # Этот хендлер можно оставить как страховку, но основной поток теперь в handle_upload_flow
    def handle_upload_media_fallback(message):
        # Дублируем логику, если вдруг сработает отдельно
        handle_upload_flow(message)


def show_admin_main_menu(bot: telebot.TeleBot, message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btns = [
        types.KeyboardButton("🔑 Открытие и закрытие салона"),
        types.KeyboardButton("📊 Работа в Yclients и Fitmost"),
        types.KeyboardButton("💵 Кассовая дисциплина и отчёты"),
        types.KeyboardButton("📣 Скрипты общения и Продажи"),
        types.KeyboardButton("📤 Загрузить медиа для инструкций"),
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
