import os
import sys
import logging
import traceback
import telebot
from telebot import types

# Импорты из наших модулей
from database import init_db, seed_data
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
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("👷 Я мастер"))
    # Можно добавить другие роли позже
    bot.reply_to(message,
                 "Привет! Добро пожаловать в команду студии Sevara. Этот бот поможет тебе быстро изучить наши стандарты, правила и сделать твою работу комфортной и безопасной. Выбери свою роль ниже:",
                 reply_markup=markup)


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
        init_db()
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
