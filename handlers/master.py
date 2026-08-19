import telebot
from telebot import types
from pathlib import Path

# --- КОНФИГУРАЦИЯ ПУТЕЙ ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PENALTIES_DIR = DATA_DIR / "penalties"


def register_master_handlers(bot):
    """
    Функция регистрации всех хендлеров для бота.
    Принимает объект bot как аргумент, чтобы избежать ошибок видимости.
    """

    # --- ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ: ПРИВЕТСТВИЕ ---
    def send_welcome(message):
        markup = types.InlineKeyboardMarkup(row_width=1)

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
        try:
            # Обработка кнопки "Регламенты"
            if call.data == "menu_regulations":
                files = [f for f in DATA_DIR.iterdir() if
                         f.is_file() and f.name.startswith("regulations_") and f.suffix == ".txt"]
                if not files:
                    bot.answer_callback_query(call.id, "Нет файлов регламентов", show_alert=True)
                    return

                markup = types.InlineKeyboardMarkup(row_width=1)
                for f in files:
                    name = f.stem.replace("regulations_", "").replace("_", " ").title()
                    markup.add(types.InlineKeyboardButton(f"📂 {name}", callback_data=f"file_reg_{f.name}"))

                markup.add(types.InlineKeyboardButton("🔙 Назад в меню", callback_data="start_over"))

                bot.edit_message_text(
                    "Выберите категорию правил:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup
                )

            # Обработка кнопки "Штрафы"
            elif call.data == "menu_penalties":
                if not PENALTIES_DIR.exists():
                    bot.answer_callback_query(call.id, "Папка со штрафами не найдена", show_alert=True)
                    return

                files = [f for f in PENALTIES_DIR.iterdir() if f.is_file() and f.suffix == ".txt"]
                if not files:
                    bot.answer_callback_query(call.id, "Нет файлов штрафов", show_alert=True)
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
                    "Выберите категорию нарушений и штрафов:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=markup
                )

            # Обработка кнопки "FAQ"
            elif call.data == "show_faq":
                faq_file = DATA_DIR / "faq.txt"
                if faq_file.exists():
                    content = faq_file.read_text(encoding="utf-8")
                    bot.send_message(call.message.chat.id, content)
                else:
                    bot.answer_callback_query(call.id, "Файл FAQ пока не создан", show_alert=True)

            # Обработка открытия файла регламентов
            elif call.data.startswith("file_reg_"):
                filename = call.data.replace("file_reg_", "")
                path = DATA_DIR / filename
                if path.exists():
                    content = path.read_text(encoding="utf-8")
                    bot.send_message(call.message.chat.id, content)
                else:
                    bot.answer_callback_query(call.id, "Файл потерян!", show_alert=True)

            # Обработка открытия файла штрафов
            elif call.data.startswith("file_pen_"):
                filename = call.data.replace("file_pen_", "")
                path = PENALTIES_DIR / filename
                if path.exists():
                    content = path.read_text(encoding="utf-8")
                    bot.send_message(call.message.chat.id, content)
                else:
                    bot.answer_callback_query(call.id, "Файл потерян!", show_alert=True)

            # Возврат в главное меню
            elif call.data == "start_over":
                send_welcome(call.message)
                # Удаляем старое сообщение с кнопками, чтобы не было дублирования
                try:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                except Exception:
                    pass  # Игнорируем ошибку, если сообщение уже нельзя удалить

            # Если ничего не подошло, просто отвечаем на нажатие (чтобы убрать часики загрузки)
            else:
                bot.answer_callback_query(call.id, "Действие обработано")

        except Exception as e:
            # Логирование ошибки, чтобы бот не падал полностью
            print(f"Ошибка в callback_handler: {e}")
            bot.answer_callback_query(call.id, "Произошла ошибка, попробуйте позже", show_alert=True)

    # --- ХЕНДЛЕР: СТЕРИЛИЗАЦИЯ (для совместимости со старыми кнопками, если есть) ---
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

    # --- ХЕНДЛЕР: ГЛАВНОЕ МЕНЮ (текстовое, если пользователь пишет вручную) ---
    @bot.message_handler(func=lambda message: message.text == "Главное меню")
    def show_main_menu(message):
        send_welcome(message)
