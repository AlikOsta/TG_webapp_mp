
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

API_TOKEN = os.getenv("API_TOKEN")
KEYS_WEB_APP_URL = os.getenv("KEYS_WEB_APP_URL")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Открыть сайт", web_app=WebAppInfo(url=KEYS_WEB_APP_URL))]
        ]
    )
    await message.answer(f"Привет. Тут будет текст и ссылка на сайт", reply_markup=keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
