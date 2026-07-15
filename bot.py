import os
import sys
import traceback
import telebot
from dotenv import load_dotenv
from database import init_db

try:
    from handlers.master import register_master_handlers, show_master_main_menu
    from handlers.admin import register_admin_handlers, show_admin_main_menu
except ImportError as e:
    print("=== ОШИБКА ИМПОРТА ===")
    print(e)
    print("Проверь: в папке handlers есть пустой файл __init__.py")
    sys.exit(1)

load_dotenv()

TOKEN = os.getenv("TELEGRAM_API_TOKEN")
print(f"[DEBUG] TOKEN = {TOKEN!r}")

if not TOKEN:
    print("=== КРИТИЧЕСКАЯ ОШИБКА ===")
    print("Не найден TELEGRAM_API_TOKEN в файле .env")
    sys.exit(1)

bot = telebot.TeleBot(TOKEN)

# --- Принудительно убираем влияние прокси (для любого способа запуска) ---
import no_proxy_session
import telebot.apihelper
telebot.apihelper._session = no_proxy_session.get_clean_session()

user_states = {}  # user_id -> state

def ensure_state_main(chat_id):
    """Гарантирует, что у пользователя есть состояние. Если нет — ставит 'main'."""
    if chat_id not in user_states:
        user_states[chat_id] = "main"

print("[DEBUG] Инициализация БД...")
try:
    init_db()
    print("[DEBUG] База данных готова.")
except Exception as e:
    print("=== ОШИБКА ПРИ ИНИЦИАЛИЗАЦИИ БД ===")
    traceback.print_exc()
    sys.exit(1)

print("[DEBUG] Регистрация хендлеров...")
try:
    register_master_handlers(bot, user_states)
    register_admin_handlers(bot, user_states)
    print("[DEBUG] Хендлеры зарегистрированы.")
except Exception as e:
    print("=== ОШИБКА ПРИ РЕГИСТРАЦИИ ХЕНДЛЕРОВ ===")
    traceback.print_exc()
    sys.exit(1)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    ensure_state_main(message.chat.id)
    user_states[message.chat.id] = "main"

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
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)


# Хендлер для главного меню — только когда состояние "main"
@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == "main")
def handle_main_menu(message):
    ensure_state_main(message.chat.id)

    text = message.text
    if text == "Я мастер":
        user_states[message.chat.id] = "Я мастер"
        show_master_main_menu(bot, message)
        return
    if text == "Я администратор":
        user_states[message.chat.id] = "Я администратор"
        show_admin_main_menu(bot, message)
        return

if __name__ == '__main__':
    print("\n=== БОТ ЗАПУЩЕН И ОЖИДАЕТ СООБЩЕНИЙ ===")
    try:
        bot.polling(non_stop=True, timeout=60)
    except Exception as e:
        print("=== ПРОИЗОШЛА ОШИБКА ВО ВРЕМЯ polling ===")
        traceback.print_exc()
