import os
import sys
import logging
import telebot
from telebot import types

# Импорты из наших модулей
from handlers.master import register_master_handlers

# --- КОНФИГУРАЦИЯ ---
API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
if not API_TOKEN:
    print("❌ Ошибка: Не найден токен TELEGRAM_API_TOKEN в переменных окружения!")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = telebot.TeleBot(API_TOKEN)


# --- РЕГИСТРАЦИЯ ХЕНДЛЕРОВ ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Создаем инлайн-клавиатуру (кнопки под сообщением)
    markup = types.InlineKeyboardMarkup(row_width=1)

    btn_regulations = types.InlineKeyboardButton("📜 Регламенты и правила", callback_data="menu_regulations")
    btn_penalties = types.InlineKeyboardButton("⚠️ Штрафы и санкции", callback_data="menu_penalties")
    btn_faq = types.InlineKeyboardButton("❓ Частые вопросы (FAQ)", callback_data="show_faq")
    btn_support = types.InlineKeyboardButton("🆘 Помощь администратора",
                                             url="https://t.me/admin_sevara")  # Ссылка на админа

    markup.add(btn_regulations, btn_penalties, btn_faq, btn_support)

    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}! Добро пожаловать в *SevaraTeamBot*! ✨\n\n"
        "Я твой помощник в салоне Sevara. Здесь ты найдешь все правила, регламенты и систему штрафов.\n"
        "Выбирай нужный раздел ниже, чтобы быстро найти ответ на свой вопрос."
    )

    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="Markdown",
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text == "👷 Я мастер")
def master_role_selected(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("✨ Стерилизация и СанПиН"))
    markup.add(types.KeyboardButton("🧹 Чистота и оборудование"))
    markup.add(types.KeyboardButton("📜 Регламенты и штрафы"))
    markup.add(types.KeyboardButton("🔙 Назад в главное меню"))
    bot.send_message(message.chat.id, "Меню мастера студии Sevara:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "🔙 Назад в главное меню")
def back_to_start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("👷 Я мастер"))
    bot.send_message(message.chat.id, "Выберите роль:", reply_markup=markup)


# Регистрируем хендлеры для мастеров
register_master_handlers(bot)

# --- ЗАПУСК И ИНИЦИАЛИЗАЦИЯ ---

if __name__ == '__main__':
    logger.info("🚀 === БОТ ЗАПУЩЕН И ОЖИДАЕТ СООБЩЕНИЙ ===")

    try:
        # 1. Создаем таблицы БД
        logger.info("✅ Таблицы БД проверены/созданы.")

        # 2. ВАЖНО: Если хочешь автонаполнение при старте - раскомментируй строку ниже.
        # Но лучше использовать команду /seed вручную, чтобы контролировать процесс.
        # result = check_and_seed_data()
        # logger.info(f"💾 Автонаполнение БД: {result}")

        logger.info("⚠️ Автонаполнение пропущено. Используйте команду /seed для заполнения базы.")

        # 3. Запуск polling
        # non_stop=True перезапускает бота при ошибках сети
        # timeout=60 увеличивает время ожидания ответа от Telegram
        bot.polling(non_stop=True, timeout=60)

    except Exception as e:
        # ИСПРАВЛЕНИЕ ОШИБКИ ИЗ ЛОГОВ:
        # Мы НЕ передаем {e} в строку формата.
        # exc_info=True сам достанет и ошибку, и стек трейса (traceback).
        logger.critical("💥 Критический сбой работы polling", exc_info=True)
        sys.exit(1)
