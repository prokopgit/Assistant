
from apscheduler.triggers.cron import CronTrigger
from database import get_random_fact
from aiogram import Bot
import os
import openai

CHANNEL_ID = os.getenv("CHANNEL_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def schedule_daily_post(scheduler, bot: Bot):
    scheduler.add_job(post_fact, CronTrigger(hour=9, minute=0, timezone="Europe/Kyiv"), args=[bot])

async def post_fact(bot: Bot):
    fact = await get_random_fact()
    if not fact and OPENAI_API_KEY:
        fact = await generate_fact()
    if fact:
        await bot.send_message(chat_id=CHANNEL_ID, text=f"📜 <b>Факт дня</b>\n{fact}")

async def generate_fact():
    try:
        openai.api_key = OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ти ентузіаст-археолог. Генеруй цікаві історії про знахідки з металошукачем в Україні."},
                {"role": "user", "content": "Придумай 1 коротку історію пошуку з металошукачем в Україні."}
            ],
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"GPT error: {e}")
        return None
