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
    sys.exit(1)

load_dotenv()

TOKEN = os.getenv("TELEGRAM_API_TOKEN")
print(f"[DEBUG] TOKEN loaded: {bool(TOKEN)}")

if not TOKEN:
    print("=== КРИТИЧЕСКАЯ ОШИБКА ===")
    print("Не найден TELEGRAM_API_TOKEN в переменных окружения")
    sys.exit(1)

bot = telebot.TeleBot(TOKEN)

user_states = {}  # user_id -> state

def ensure_state_main(chat_id):
    if chat_id not in user_states:
        user_states[chat_id]
