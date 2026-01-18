#!/usr/bin/env python3
"""
Главный файл для запуска Flask приложения и Telegram бота
"""
import threading
import asyncio
import logging
from app import app, Config
from bot import bot, dp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MainRunner")

def run_flask():
    """Запуск Flask приложения"""
    logger.info(f"🚀 Flask запускается на http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)

async def run_bot():
    """Запуск Telegram бота"""
    logger.info(f"🤖 Telegram бот запускается (TOKEN: {Config.BOT_TOKEN[:20]}...)")
    logger.info(f"📱 Web App URL: https://zoved-site-maker--liosliosefr.replit.app/auth_start.html")
    await dp.start_polling(bot)

def run_bot_sync():
    """Синхронный запуск бота"""
    asyncio.run(run_bot())

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🎯 Запуск Telegram Web App + Бот")
    logger.info("=" * 60)
    
    # Запускаем Flask в отдельном потоке (с use_reloader=False)
    flask_thread = threading.Thread(target=lambda: app.run(
        host=Config.FLASK_HOST, 
        port=Config.FLASK_PORT, 
        debug=False,
        use_reloader=False
    ), daemon=True)
    flask_thread.start()
    logger.info(f"✅ Flask запущен на http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    
    # Запускаем бота в главном потоке
    try:
        run_bot_sync()
    except KeyboardInterrupt:
        logger.info("⏹️  Остановка приложения...")
