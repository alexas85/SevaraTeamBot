import telebot
from telebot import types
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PENALTIES_DIR = DATA_DIR / "penalties"


def register_master_handlers(bot):
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("📜 Регламенты и штрафы")
        markup.add("✨ Стерилизация и СанПиН")
        bot.reply_to(message, "Выберите раздел:", reply_markup=markup)

    # --- ГЛАВНОЕ МЕНЮ ШТРАФОВ И РЕГЛАМЕНТОВ ---
    @bot.message_handler(func=lambda message: message.text == "📜 Регламенты и штрафы")
    def show_main_regulations_menu(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("📖 Регламенты (правила работы)")
        markup.add("⚠️ Штрафы и санкции")
        markup.add("🔙 Назад в главное меню")
        bot.send_message(message.chat.id, "Что хотите посмотреть?", reply_markup=markup)

    # --- ПОДМЕНЮ РЕГЛАМЕНТОВ (старый функционал) ---
    @bot.message_handler(func=lambda message: message.text == "📖 Регламенты (правила работы)")
    def show_regulations_submenu(message):
        if not DATA_DIR.exists():
            bot.reply_to(message, "❌ Папка data/ не найдена.")
            return

        files = [f for f in DATA_DIR.iterdir() if
                 f.is_file() and f.name.startswith("regulations_") and f.suffix == ".txt"]
        if not files:
            bot.reply_to(message, "❌ Нет файлов регламентов.")
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for f in files:
            name = f.stem.replace("regulations_", "").replace("_", " ").title()
            markup.add(f"📂 {name}")
        markup.add("🔙 Назад")
        bot.send_message(message.chat.id, "Выберите категорию правил:", reply_markup=markup)

    # --- ПОДМЕНЮ ШТРАФОВ (НОВЫЙ ФУНКЦИОНАЛ) ---
    @bot.message_handler(func=lambda message: message.text == "⚠️ Штрафы и санкции")
    def show_penalties_menu(message):
        if not PENALTIES_DIR.exists():
            bot.reply_to(message, "❌ Папка data/penalties/ не найдена. Проверьте файлы.")
            return

        files = [f for f in PENALTIES_DIR.iterdir() if f.is_file() and f.suffix == ".txt"]
        if not files:
            bot.reply_to(message, "❌ Нет файлов со штрафами.")
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

        # Формируем понятные названия кнопок из имен файлов
        for f in files:
            # Убираем префикс penalties_ и расширение, делаем читаемым
            raw_name = f.stem
            # Простая замена для кнопок
            display_name = raw_name.replace("quality_and_redo", "Качество и переделки") \
                .replace("attendance", "График и опоздания") \
                .replace("property_and_tools", "Инструменты и имущество") \
                .replace("hygiene_violations", "Стерильность и СанПиН") \
                .replace("cash_and_complaints", "Деньги, чеки и жалобы") \
                .replace("workplace_cleanliness", "Уборка рабочего места")

            markup.add(f"⚖️ {display_name}")

        markup.add("🔙 Назад")
        bot.send_message(message.chat.id, "Выберите категорию нарушений и штрафов:", reply_markup=markup)

    # --- ОБРАБОТКА КНОПОК РЕГЛАМЕНТОВ (старое) ---
    @bot.message_handler(func=lambda message: message.text.startswith("📂 "))
    def show_regulations_category(message):
        category_display = message.text.replace("📂 ", "")
        search_key = category_display.lower().replace(" ", "_")
        target_file = None

        for f in DATA_DIR.iterdir():
            if f.is_file() and f.name.startswith("regulations_") and f.suffix == ".txt":
                if search_key in f.name:
                    target_file = f
                    break

        if not target_file:
            bot.reply_to(message, "Файл не найден.")
            return

        try:
            content = target_file.read_text(encoding="utf-8")
            bot.send_message(message.chat.id, content)
        except Exception as e:
            bot.reply_to(message, f"Ошибка чтения: {e}")

    # --- ОБРАБОТКА КНОПОК ШТРАФОВ (новое) ---
    @bot.message_handler(func=lambda message: message.text.startswith("⚖️ "))
    def show_penalty_category(message):
        category_display = message.text.replace("⚖️ ", "")
        # Ищем файл по части названия
        search_key = category_display.lower().replace(" ", "_").replace("-", "_")

        target_file = None
        for f in PENALTIES_DIR.iterdir():
            if f.is_file() and f.suffix == ".txt":
                # Проверяем, содержится ли ключ в имени файла
                if search_key in f.name:
                    target_file = f
                    break

        if not target_file:
            bot.reply_to(message, f"Не удалось найти файл для категории: {category_display}")
            return

        try:
            content = target_file.read_text(encoding="utf-8")
            bot.send_message(message.chat.id, content)
        except Exception as e:
            bot.reply_to(message, f"Ошибка чтения файла: {e}")

    # --- КНОПКА СТЕРИЛИЗАЦИИ (старое) ---
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

    # --- НАЗАД ---
    @bot.message_handler(func=lambda message: message.text == "🔙 Назад" or message.text == "🔙 Назад в главное меню")
    def go_back(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("📜 Регламенты и штрафы")
        markup.add("✨ Стерилизация и СанПиН")
        bot.send_message(message.chat.id, "Главное меню:", reply_markup=markup)
