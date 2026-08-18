import os
import sys
import logging
import traceback
import telebot
from dotenv import load_dotenv

# Импорты из локальных модулей
from config import STATE_MAIN, STATE_ROLE_MASTER, STATE_ROLE_ADMIN
from handlers.master import register_master_handlers, show_master_main_menu
from handlers.admin import register_admin_handlers, show_admin_main_menu
from database import init_db, check_and_seed_data

# --- НАСТРОЙКА ЛОГИРОВАНИЯ ---
LOG_FORMAT = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

logger = logging.getLogger('SevaraTeamBot')
logger.setLevel(logging.INFO)

# 1. Handler для вывода в консоль (stdout) — критично для Dada Console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
console_handler.setFormatter(console_formatter)

# 2. Handler для записи в файл (для детального расследования)
try:
    file_handler = logging.FileHandler('bot.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(f'{LOG_FORMAT} | {DATE_FORMAT}')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
except Exception as e:
    # Если нет прав на запись файла, логируем ошибку в консоль
    print(f"⚠️ Не удалось создать файл логов bot.log: {e}")

logger.addHandler(console_handler)

# Загружаем переменные окружения
load_dotenv()

# --- ПРОВЕРКА ТОКЕНА ---
TOKEN = os.getenv("TELEGRAM_API_TOKEN")

if not TOKEN:
    logger.critical("❌ КРИТИЧЕСКАЯ ОШИБКА: TELEGRAM_API_TOKEN не найден!")
    logger.critical("Проверьте настройки переменных окружения в Dada Console.")
    sys.exit(1)

logger.info("✅ Токен успешно загружен.")

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# Хранилище состояний пользователей: chat_id -> state
user_states = {}


def ensure_state_main(chat_id):
    """Гарантирует, что у пользователя есть состояние STATE_MAIN."""
    if chat_id not in user_states:
        user_states[chat_id] = STATE_MAIN


# --- ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ ---
logger.info("🗄️ Инициализация базы данных...")
try:
    # 1. Создаем таблицы, если их нет
    init_db()
    logger.info("✅ Таблицы БД проверены/созданы.")

    # 2. АВТОМАТИЧЕСКОЕ НАПОЛНЕНИЕ ДАННЫМИ (СЕЙДИНГ)
    # Если таблица regulations пуста, эта функция заполнит её тестовыми данными
    check_and_seed_data()
    logger.info("✅ Проверка и наполнение данных выполнено.")

except Exception as e:
    logger.critical(f"❌ FATAL ERROR: Не удалось инициализировать БД: {e}")
    logger.critical(traceback.format_exc())
    sys.exit(1)

logger.info("📜 Регистрация хендлеров (мастера и админы)...")
try:
    register_master_handlers(bot, user_states)
    register_admin_handlers(bot, user_states)
    logger.info("✅ Хендлеры успешно зарегистрированы.")
except Exception as e:
    logger.critical(f"❌ FATAL ERROR: Ошибка при регистрации хендлеров: {e}")
    logger.critical(traceback.format_exc())
    sys.exit(1)


# --- ХЕНДЛЕРЫ БОТА ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Обработчик команды /start"""
    chat_id = message.chat.id
    ensure_state_main(chat_id)
    user_states[chat_id] = STATE_MAIN

    welcome_text = (
        "Привет! Добро пожаловать в команду студии Sevara. "
        "Этот бот поможет тебе быстро изучить наши стандарты, правила "
        "и сделать твою работу комфортной и безопасной. "
        "Выбери свою роль ниже:"
    )

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_master = telebot.types.KeyboardButton("Я мастер")
    btn_admin = telebot.types.KeyboardButton("Я администратор")
    markup.add(btn_master, btn_admin)

    try:
        bot.send_message(chat_id, welcome_text, reply_markup=markup)
        logger.info(f"👤 Пользователь {chat_id} нажал /start")
    except Exception as e:
        logger.error(f"Ошибка отправки приветствия пользователю {chat_id}: {e}")


@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == STATE_MAIN)
def handle_main_menu(message):
    """Обработка выбора роли в главном меню"""
    chat_id = message.chat.id
    text = message.text

    ensure_state_main(chat_id)

    if text == "Я мастер":
        user_states[chat_id] = STATE_ROLE_MASTER
        try:
            show_master_main_menu(bot, message)
            logger.info(f"👷 Пользователь {chat_id} выбрал роль: МАСТЕР")
        except Exception as e:
            logger.error(f"Ошибка показа меню мастера для {chat_id}: {e}")
            bot.send_message(chat_id, "Произошла ошибка при загрузке меню. Попробуйте позже.")
        return

    if text == "Я администратор":
        user_states[chat_id] = STATE_ROLE_ADMIN
        try:
            show_admin_main_menu(bot, message)
            logger.info(f"👮 Пользователь {chat_id} выбрал роль: АДМИН")
        except Exception as e:
            logger.error(f"Ошибка показа меню админа для {chat_id}: {e}")
            bot.send_message(chat_id, "Произошла ошибка при загрузке меню. Попробуйте позже.")
        return

    # Если нажали что-то лишнее в главном меню
    bot.send_message(chat_id, "Пожалуйста, выберите роль с помощью кнопок ниже.")


# --- ЗАПУСК ---
if __name__ == '__main__':
    logger.info("🚀 === БОТ ЗАПУЩЕН И ОЖИДАЕТ СООБЩЕНИЙ ===")
    try:
        # non_stop=True перезапускает polling при ошибках сети
        # timeout=60 увеличивает время ожидания ответа от Telegram
        bot.polling(non_stop=True, timeout=60)
    except Exception as e:
        logger.critical(f"💥 Критический сбой работы polling: {e}", exc_info=True)
        sys.exit(1)
