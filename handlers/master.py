import telebot
from telebot import types
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # подняться на 2 уровня вверх до корня проекта
DATA_DIR = BASE_DIR / "data"

def register_master_handlers(bot):

    # Команда /seed — теперь ничего не делает, но можно оставить как заглушку
    @bot.message_handler(commands=['seed'])
    def handle_seed(message):
        bot.reply_to(message, "В этой версии данные хранятся в текстовых файлах (папка data/).")

    # Кнопка "📜 Регламенты и штрафы" — показывает список категорий по файлам
    @bot.message_handler(func=lambda message: message.text == "📜 Регламенты и штрафы")
    def show_regulations_menu(message):
        if not DATA_DIR.exists():
            bot.reply_to(message, "❌ Папка data/ не найдена. Проверьте структуру проекта.")
            return

        # Ищем файлы с префиксом regulations_
        files = [f for f in DATA_DIR.iterdir() if f.is_file() and f.name.startswith("regulations_") and f.suffix == ".txt"]

        if not files:
            bot.reply_to(
                message,
                "⚠️ В папке data/ нет файлов регламентов.\n"
                "Создайте хотя бы один файл вида regulations_<категория>.txt"
            )
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        for f in files:
            # Из имени файла делаем читаемое название: regulations_hygiene.txt -> "Гигиена и санитария"
            name = f.stem.replace("regulations_", "").replace("_", " ").title()
            markup.add(types.KeyboardButton(f"📂 {name}"))

        markup.add(types.KeyboardButton("🔙 Назад в меню мастера"))
        bot.send_message(message.chat.id, "Выберите категорию регламентов:", reply_markup=markup)

    # Обработка кнопок вида "📂 Гигиена И Санитария" — читаем соответствующий файл
    @bot.message_handler(func=lambda message: message.text.startswith("📂 "))
    def show_regulations_category(message):
        category_display = message.text.replace("📂 ", "")
        # Обратно превращаем читаемое имя в имя файла: "Гигиена И Санитария" -> regulations_гигиена_и_санитария.txt
        # Но проще: искать по части имени. Для простоты сделаем так:
        # Мы ищем файл, который содержит в имени часть категории в нижнем регистре без пробелов.
        search_key = category_display.lower().replace(" ", "_")

        target_file = None
        for f in DATA_DIR.iterdir():
            if f.is_file() and f.name.startswith("regulations_") and f.suffix == ".txt":
                if search_key in f.name:
                    target_file = f
                    break

        if not target_file:
            bot.reply_to(message, f"❌ Не удалось найти файл для категории: {category_display}")
            return

        try:
            content = target_file.read_text(encoding="utf-8")
            bot.send_message(message.chat.id, content, parse_mode=None)  # parse_mode не нужен для простого текста
        except Exception as e:
            bot.reply_to(message, f"Ошибка чтения файла: {e}")

    # Кнопка "✨ Стерилизация и СанПиН" — читает отдельный файл
    @bot.message_handler(func=lambda message: message.text == "✨ Стерилизация и СанПиН")
    def handle_sterilization(message):
        ster_file = DATA_DIR / "sterilization.txt"
        if not ster_file.exists():
            bot.reply_to(message, "❌ Файл data/sterilization.txt не найден.")
            return
        try:
            text = ster_file.read_text(encoding="utf-8")
            bot.send_message(message.chat.id, text, parse_mode=None)
        except Exception as e:
            bot.reply_to(message, f"Ошибка чтения sterilization.txt: {e}")
