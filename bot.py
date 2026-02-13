import logging
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

# ============ КОНФИГУРАЦИЯ ============
TOKEN = os.getenv("TOKEN")  # ← Берём токен из переменной окружения
if not TOKEN:
    raise ValueError("❌ Переменная окружения TOKEN не установлена!")

WEB_APP_URL = "https://bebronuxaye.github.io/dedvpn-web/"
LOG_FILE = "users.txt"

# ============ НАСТРОЙКА ЛОГИРОВАНИЯ ============
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============ ФУНКЦИЯ ЛОГИРОВАНИЯ ============
def log_user(user):
    """Логирует информацию о пользователе в текстовый файл"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        username = f"@{user.username}" if user.username else "без username"
        full_name = f"{user.first_name} {user.last_name}".strip()
        
        log_entry = (
            f"[{timestamp}] ID: {user.id} | Username: {username} | "
            f"Имя: {full_name} | Язык: {user.language_code}\n"
        )
        
        # Дополнительная запись в файл (на случай проблем с настройкой логгера)
        with open("users_raw.txt", 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        logger.info(f"Залогирован пользователь: {user.id} ({username})")
    
    except Exception as e:
        logger.error(f"Ошибка логирования: {e}")

# ============ ОБРАБОТЧИК /start ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение с кнопкой Web App"""
    user = update.effective_user
    log_user(user)
    
    keyboard = [[InlineKeyboardButton(
        text="🚀 Начать пользоваться VPN",
        web_app=WebAppInfo(url=WEB_APP_URL)
    )]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "🔐 <b>DedVPN</b>\n\n"
        "Добро пожаловать в самый быстрый и безопасный VPN сервис!\n\n"
        "Нажмите кнопку ниже, чтобы начать пользоваться BarryVPN:"
    )
    
    await update.message.reply_text(
        text=welcome_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

# ============ ГЛАВНАЯ ФУНКЦИЯ ============
def main():
    logger.info(f"✅ Запуск бота с токеном: {TOKEN[:5]}...")
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    logger.info("✅ Бот запущен и готов к работе")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()

