import asyncio
import logging
import os
import random

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database import init_db, save_geo, get_random_geo, get_all_geo, save_fact, get_all_facts, get_random_fact, delete_fact
from geo_utils import extract_geo_from_photo
from scheduler import schedule_daily_post
from config import TELEGRAM_TOKEN, CHANNEL_ID, OPENAI_API_KEY, GEMINI_API_KEY
from gpt_utils import get_smart_reply

from aiogram.client.default import DefaultBotProperties

bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
scheduler = AsyncIOScheduler()

start_messages = [
    "👋 Бувай здоров, колего по розкопках!",
    "🔍 Шурфан на зв’язку! Що сьогодні викопаємо?",
    "🏺 Я тут, з пилкою й щіткою. Готовий до пригод!",
    "🗺️ Схоже, хтось шукає скарби? Я допоможу!",
    "💬 Запитай що хочеш, тільки не чіпай мій ржавий казан!"
]

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(random.choice(start_messages))

@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "<b>📜 Мої команди:</b>\n"
        "/geo — випадкові координати\n"
        "/listgeo — всі координати\n"
        "/addfact <текст> — додати історію\n"
        "/listfacts — всі історії\n"
        "/deletefact <id> — видалити історію\n"
        "/ping — перевірити чи я живий"
    )

@dp.message(Command("ping"))
async def ping_cmd(message: Message):
    await message.answer("✅ Бот активний і слухає.")

@dp.message(Command("geo"))
async def geo_cmd(message: Message):
    coord = await get_random_geo()
    if coord:
        await message.answer(f"🗺️ Випадкові координати:\nhttps://maps.google.com/?q={coord}")
    else:
        await message.answer("База координат порожня.")

@dp.message(Command("listgeo"))
async def list_geo(message: Message):
    coords = await get_all_geo()
    if not coords:
        await message.answer("⛔ Немає збережених координат.")
        return
    text = "🗺️ Збережені координати:\n"
    for i, c in enumerate(coords, 1):
        text += f"{i}. https://maps.google.com/?q={c}\n"
    await message.answer(text)

@dp.message(Command("addfact"))
async def add_fact(message: Message):
    content = message.text[len("/addfact"):].strip()
    if not content:
        await message.answer("⚠️ Введи текст після команди /addfact")
        return
    await save_fact(content)
    await message.answer("✅ Історію додано!")

@dp.message(Command("listfacts"))
async def list_facts(message: Message):
    facts = await get_all_facts()
    if not facts:
        await message.answer("База історій порожня.")
        return
    msg = "\n\n".join([f"{r['id']}. {r['text']}" for r in facts])
    await message.answer(f"📚 Усі історії:\n{msg}")

@dp.message(Command("deletefact"))
async def delete_fact_cmd(message: Message):
    parts = message.text.strip().split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("⚠️ Вкажи ID історії: /deletefact <id>")
        return
    result = await delete_fact(int(parts[1]))
    if result:
        await message.answer("🗑 Історію видалено.")
    else:
        await message.answer("❌ Такої історії не знайдено.")

@dp.message(F.photo)
async def handle_photo(message: Message):
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    path = f"temp_{photo.file_id}.jpg"
    await bot.download_file(file.file_path, destination=path)
    coords = extract_geo_from_photo(path)
    os.remove(path)
    if coords:
        await save_geo(coords)
        await message.answer(f"✅ Координати збережено: {coords}")
    else:
        await message.answer("❌ Не знайдено координат у цьому фото.")

@dp.message(F.text)
async def gpt_reply(message: Message):
    reply = await get_smart_reply(message.text)
    await message.answer(reply)

async def main():
    await init_db()
    schedule_daily_post(scheduler, bot)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())