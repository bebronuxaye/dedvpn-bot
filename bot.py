import logging
import os
import requests
from datetime import datetime
from urllib.parse import quote
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

# ============ КОНФИГУРАЦИЯ ============
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("❌ Переменная окружения TOKEN не установлена!")

# Адрес вашего ВПН-сервера (ЗАМЕНИТЕ НА ВАШ РЕАЛЬНЫЙ IP!)
VPN_SERVER_API = "http://91.108.241.69:5000/api/generate"

WEB_APP_BASE_URL = "https://bebronuxaye.github.io/dedvpn-web/"
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
        
        with open("users_raw.txt", 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        logger.info(f"Залогирован пользователь: {user.id} ({username})")
    
    except Exception as e:
        logger.error(f"Ошибка логирования: {e}")

# ============ ФУНКЦИЯ ГЕНЕРАЦИИ КОНФИГА ============
def generate_vpn_config(user_id):
    """Запрашивает конфиг у вашего сервера"""
    try:
        response = requests.post(
            VPN_SERVER_API,
            json={'user_id': str(user_id)},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get('success') and 'happ_url' in data:
            # happ_url уже закодирован (например: ss%3A%2F%2F...)
            return data['happ_url']
        else:
            logger.error(f"Сервер вернул ошибку: {data}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка запроса к серверу: {e}")
        return None
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
        return None

# ============ ОБРАБОТЧИК /start ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерирует конфиг и открывает Web App с параметром config"""
    user = update.effective_user
    log_user(user)
    
    # Генерируем конфиг для пользователя
    config = generate_vpn_config(user.id)
    
    if not config:
        await update.message.reply_text(
            "❌ Ошибка генерации конфига. Сервер недоступен. Попробуйте позже.",
            parse_mode='HTML'
        )
        return
    
    # Формируем URL Web App с конфигом (БЕЗ дополнительного кодирования!)
    # config уже закодирован как ss%3A%2F%2F...
    web_app_url = f"{WEB_APP_BASE_URL}?config={config}"
    
    logger.info(f"Сформирован URL для пользователя {user.id}: {web_app_url[:80]}...")
    
    keyboard = [[InlineKeyboardButton(
        text="🚀 Начать пользоваться VPN",
        web_app=WebAppInfo(url=web_app_url)
    )]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "🔐 <b>DedVPN</b>\n\n"
        "Ваш персональный конфиг создан!\n"
        "Нажмите кнопку ниже для подключения:"
    )
    
    await update.message.reply_text(
        text=welcome_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

# ============ ГЛАВНАЯ ФУНКЦИЯ ============
def main():
    logger.info(f"✅ Запуск бота...")
    logger.info(f"📡 API сервера: {VPN_SERVER_API}")
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    logger.info("✅ Бот запущен и готов к работе")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()

