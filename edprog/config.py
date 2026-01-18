import os

class Config:
    # --- ДАННЫЕ TELEGRAM (my.telegram.org) ---
    TELEGRAM_API_ID = 32547469           # Твой API_ID
    TELEGRAM_API_HASH = '0dc818f0186f243ce3ca4bc3d5af96e3' # Твой API_HASH

    API_ID = TELEGRAM_API_ID
    API_HASH = TELEGRAM_API_HASH

    # --- ДАННЫЕ БОТА ---
    BOT_TOKEN = '8113589352:AAH-hc9HLxS0n86xQj7P6YYfkJ3XsOWiPUk'
    ADMIN_ID = 8100764265

    # --- НАСТРОЙКИ FLASK ---
    SECRET_KEY = 'не_меняй' 
    
    FLASK_HOST = '0.0.0.0'
    # На Replit используется PORT переменная
    FLASK_PORT = int(os.environ.get('PORT', '3000'))
    FLASK_DEBUG = False
    SESSION_DIR = 'sessions'