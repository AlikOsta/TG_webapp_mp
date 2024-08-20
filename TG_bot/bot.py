
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv, find_dotenv
import jwt

load_dotenv(find_dotenv())

API_TOKEN = os.getenv("API_TOKEN")
KEYS_WEB_APP_URL = os.getenv("KEYS_WEB_APP_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    print(message)
    telegram_id = message.from_user.id
    user_name = message.from_user.first_name
    tg_name = message.from_user.username
    # user_photo = message.from_user.profile_photo

    # Генерируем JWT токен
    payload = {"telegram_id": telegram_id, "user_name": user_name, "tg_name": tg_name}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    print(token)
    web_app_url = f"{KEYS_WEB_APP_URL}?token={token}"
    print(web_app_url)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Открыть сайт", web_app=WebAppInfo(url=web_app_url))]]
    )

    await message.answer("Привет! Нажми на кнопку ниже, чтобы открыть сайт.", reply_markup=keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



