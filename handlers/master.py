import telebot
from telebot import types
from pathlib import Path
import logging

# Настройка логов, чтобы видеть в консоли, что происходит при нажатии
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- КОНФИГУРАЦИЯ ПУТЕЙ ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PENALTIES_DIR = DATA_DIR / "penalties"


def register_master_handlers(bot):
    """
    Регистрирует все хендлеры для бота.
    """

    # --- ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ: ПРИВЕТСТВИЕ ---
    def send_welcome(message):
        markup = types.InlineKeyboardMarkup(row_width=1)

        # ВАЖНО: callback_data должен точно совпадать с тем, что ждет handler
        btn_regulations = types.InlineKeyboardButton("📜 Регламенты и правила", callback_data="menu_regulations")
        btn_penalties = types.InlineKeyboardButton("⚠️ Штрафы и санкции", callback_data="menu_penalties")
        btn_faq = types.InlineKeyboardButton("❓ Частые вопросы (FAQ)", callback_data="show_faq")
        btn_support = types.InlineKeyboardButton("🆘 Помощь администратора", url="https://t.me/admin_sevara")

        markup.add(btn_regulations, btn_penalties, btn_faq, btn_support)

        welcome_text = (
            f"👋 Привет, {message.from_user.first_name}! Добро пожаловать в *SevaraTeamBot*! ✨\n\n"
            "Я твой помощник в салоне Sevara. Здесь ты найдешь все правила, регламенты и систему штрафов.\n"
            "Выбирай нужный раздел ниже."
        )

        bot.send_message(
            message.chat.id,
            welcome_text,
            parse_mode="Markdown",
            reply_markup=markup
        )

    # --- ХЕНДЛЕР: КОМАНДА /START ---
    @bot.message_handler(commands=['start'])
    def start_command(message):
        send_welcome(message)

    # --- ХЕНДЛЕР: ОБРАБОТКА CALLBACK (КНОПКИ) ---
    @bot.callback_query_handler(func=lambda call: True)
    def callback_handler(call):
        logging.info(f"Пользователь {call.from_user.id} нажал кнопку: {call.data}")

        try:
            # 1. Обработка кнопки "Регламенты"
            if call.data == "menu_regulations":
                logging.info("Открываем меню регламентов...")

                # Ищем файлы, которые начинаются на 'regulations_'
                files = [f for f in DATA_DIR.iterdir() if
                         f.is_file() and f.name.startswith("regulations_") and f.suffix == ".txt"]

                if not files:
                    logging.warning("Папка регламентов пуста или файлы не найдены!")
                    # Показываем красивое уведомление сверху
                    bot.answer_callback_query(call.id,
                                              "📭 Сейчас нет загруженных регламентов. Обратитесь к администратору.",
                                              show_alert=True)

                    # Опционально: можно отправить сообщение в чат
                    # bot.send_message(call.message.chat.id, "К сожалению, сейчас нет файлов с регламентами.")
                    return

                markup = types.InlineKeyboardMarkup(row_width=1)
                for f in files:
                    # Убираем префикс regulations_ и подчеркивания для красивого названия
                    name = f.stem.replace("regulations_", "").replace("_", " ").title()
                    markup.add(types.InlineKeyboardButton(f"📂 {name}", callback_data=f"file_reg_{f.name}"))

                markup.add(types.InlineKeyboardButton("🔙 Назад в меню", callback_data="start_over"))

                bot.edit_message_text(
                    "📚 Выберите категорию регламентов:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup
                )

            # 2. Обработка кнопки "Штрафы"
            elif call.data == "menu_penalties":
                logging.info("Открываем меню штрафов...")

                if not PENALTIES_DIR.exists():
                    logging.error("Папка penalties не существует!")
                    bot.answer_callback_query(call.id, "❌ Папка со штрафами не найдена на сервере.", show_alert=True)
                    return

                files = [f for f in PENALTIES_DIR.iterdir() if f.is_file() and f.suffix == ".txt"]
                if not files:
                    logging.warning("В папке penalties нет файлов!")
                    bot.answer_callback_query(call.id, "📭 Сейчас нет загруженных штрафов.", show_alert=True)
                    return

                markup = types.InlineKeyboardMarkup(row_width=1)
                name_map = {
                    "quality_and_redo.txt": "Качество и переделки",
                    "attendance.txt": "График и опоздания",
                    "property_and_tools.txt": "Инструменты и имущество",
                    "hygiene_violations.txt": "Стерильность и СанПиН",
                    "cash_and_complaints.txt": "Деньги, чеки и жалобы",
                    "workplace_cleanliness.txt": "Уборка рабочего места"
                }

                for f in files:
                    display_name = name_map.get(f.name, f.stem.replace("_", " ").title())
                    markup.add(types.InlineKeyboardButton(f"⚖️ {display_name}", callback_data=f"file_pen_{f.name}"))

                markup.add(types.InlineKeyboardButton("🔙 Назад в меню", callback_data="start_over"))

                bot.edit_message_text(
                    "⚠️ Выберите категорию нарушений и штрафов:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup
                )

            # 3. Обработка кнопки "FAQ"
            elif call.data == "show_faq":
                faq_file = DATA_DIR / "faq.txt"
                if faq_file.exists():
                    content = faq_file.read_text(encoding="utf-8")
                    bot.send_message(call.message.chat.id, content)
                else:
                    bot.answer_callback_query(call.id, "Файл FAQ пока не создан", show_alert=True)

            # 4. Открытие файла регламентов
            elif call.data.startswith("file_reg_"):
                filename = call.data.replace("file_reg_", "")
                path = DATA_DIR / filename
                if path.exists():
                    content = path.read_text(encoding="utf-8")
                    bot.send_message(call.message.chat.id, content)
                else:
                    bot.answer_callback_query(call.id, "Файл потерян!", show_alert=True)

            # 5. Открытие файла штрафов
            elif call.data.startswith("file_pen_"):
                filename = call.data.replace("file_pen_", "")
                path = PENALTIES_DIR / filename
                if path.exists():
                    content = path.read_text(encoding="utf-8")
                    bot.send_message(call.message.chat.id, content)
                else:
                    bot.answer_callback_query(call.id, "Файл потерян!", show_alert=True)

            # 6. Возврат в главное меню
            elif call.data == "start_over":
                send_welcome(call.message)
                try:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                except Exception:
                    pass

            else:
                # Если нажали какую-то неизвестную кнопку
                logging.warning(f"Неизвестный callback_data: {call.data}")
                bot.answer_callback_query(call.id, "Действие обработано", show_alert=False)

        except Exception as e:
            logging.error(f"Критическая ошибка в callback_handler: {e}", exc_info=True)
            bot.answer_callback_query(call.id, "Произошла ошибка сервера. Попробуйте позже.", show_alert=True)

    # --- ХЕНДЛЕРЫ ДЛЯ СТАРЫХ ТЕКСТОВЫХ КНОПОК (НА ВСЯКИЙ СЛУЧАЙ) ---
    # Если у тебя где-то в коде остались обычные кнопки (не inline), которые пишут текст в чат,
    # этот блок их обработает, чтобы бот не молчал.

    @bot.message_handler(
        func=lambda message: message.text in ["Главное меню", "📜 Регламенты и правила", "⚠️ Штрафы и санкции"])
    def handle_text_buttons(message):
        logging.info(f"Пользователь нажал текстовую кнопку: {message.text}")
        send_welcome(message)

    @bot.message_handler(func=lambda message: message.text == "✨ Стерилизация и СанПиН")
    def handle_sterilization(message):
        ster_file = DATA_DIR / "sterilization.txt"
        if not ster_file.exists():
            bot.reply_to(message, "❌ Файл data/sterilization.txt не найден.")
            return
        try:
            text = ster_file.read_text(encoding="utf-8")
            bot.send_message(message.chat.id, text)
        except Exception as e:
            bot.reply_to(message, f"Ошибка чтения: {e}")
