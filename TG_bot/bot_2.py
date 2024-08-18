# telegram_bot.py

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.filters import CommandStart
import jwt

TELEGRAM_BOT_TOKEN = "your-telegram-bot-token"
JWT_SECRET = "your-jwt-secret-key"
WEB_APP_URL = "https://your-site.com/web-app/"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username

    # Генерируем JWT токен
    payload = {"user_id": user_id, "username": username}
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    web_app_url = f"{WEB_APP_URL}?token={token}"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Открыть сайт", web_app=WebAppInfo(url=web_app_url))]]
    )

    await message.answer("Привет! Нажми на кнопку ниже, чтобы открыть сайт.", reply_markup=keyboard)
