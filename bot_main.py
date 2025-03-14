from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from use_news import fetch_news
import logging
import asyncio
import config

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Токен вашего бота
API_TOKEN = config.TOKEN

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Создаем маршрутизатор
router = Router()

# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text="Привет!")
    builder.button(text="Новости")
    await message.answer(
        "Привет! Я ваш бот. Выберите действие:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )

# Обработчик текстовых сообщений
@router.message(F.text == "Привет!")
async def echo_hello(message: types.Message):
    await message.answer(f"Привет, человек! {message.from_user.full_name}")

@router.message(F.text == "Новости")
async def echo_help(message: types.Message):
    await message.answer("Ожидайте Новости подгружаются")
    news = fetch_news()
    if news is None:
        await message.answer("Ошибка загрузки новостей")
    else:
        for new in news:
            await message.answer(f"{new[0]}, {new[1]}, {new[2]}, {new[3]}")

# Регистрируем маршрутизатор в диспетчере
dp.include_router(router)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())