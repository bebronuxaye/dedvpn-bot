import logging
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackContext

# ============ КОНФИГУРАЦИЯ ============
TOKEN = os.getenv("TOKEN")  # ← ЗАМЕНИТЕ НА ВАШ ТОКЕН
WEB_APP_URL = "https://bebronuxaye.github.io/dedvpn-web/"  # ← ВАШ GitHub Pages URL
LOG_FILE = "users.txt"  # Файл для логирования

# ============ НАСТРОЙКА ЛОГИРОВАНИЯ ============
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============ ФУНКЦИЯ ЛОГИРОВАНИЯ ============
def log_user(user):
    """Логирует информацию о пользователе в текстовый файл"""
    try:
        # Форматируем данные
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        username = f"@{user.username}" if user.username else "без username"
        full_name = f"{user.first_name} {user.last_name}".strip()
        
        # Формируем строку лога
        log_entry = (
            f"[{timestamp}] ID: {user.id} | Username: {username} | "
            f"Имя: {full_name} | Язык: {user.language_code}\n"
        )
        
        # Записываем в файл
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        logger.info(f"Залогирован пользователь: {user.id} ({username})")
    
    except Exception as e:
        logger.error(f"Ошибка логирования: {e}")

# ============ ОБРАБОТЧИК /start ============
async def start(update: Update, context: CallbackContext):
    """Отправляет приветственное сообщение с кнопкой Web App"""
    user = update.effective_user
    log_user(user)  # Логируем пользователя
    
    # Кнопка Web App
    keyboard = [
        [
            InlineKeyboardButton(
                text="🚀 Начать пользоваться VPN",
                web_app=WebAppInfo(url=WEB_APP_URL)
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Приветственное сообщение
    welcome_text = (
        "🔐 <b>Ded VPN</b>\n\n"
        "Добро пожаловать в самый быстрый и безопасный VPN сервис!\n\n"
        "Нажмите кнопку ниже, чтобы начать пользоваться Ded VPN:"
    )
    
    await update.message.reply_text(
        text=welcome_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

# ============ ГЛАВНАЯ ФУНКЦИЯ ============
def main():
    """Запуск бота"""
    # Создаем файл лога, если его нет
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            f.write("=== ЛОГ ПОЛЬЗОВАТЕЛЕЙ BARRYVPN ===\n")
            f.write("Дата запуска бота: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
        logger.info(f"Создан файл логирования: {LOG_FILE}")
    
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчик
    application.add_handler(CommandHandler("start", start))
    
    # Запускаем бота
    logger.info("✅ Бот запущен. Логирование пользователей включено.")
    logger.info(f"📁 Файл логов: {os.path.abspath(LOG_FILE)}")
    application.run_polling()

if __name__ == '__main__':

    main()


