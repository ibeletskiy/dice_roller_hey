import aiohttp
import asyncio
import logging
import sys
import os
import pytz

from db import DataBase

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from random import randint

from config import API_TOKEN

dp = Dispatcher()

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

db = DataBase()

scheduler = AsyncIOScheduler(timezone=pytz.utc)

def get_dices(text: str):
    dice, count = list(map(int, text.split()))
    return [[dice, count]]

async def delete_message(message: Message, bot_message: Message):
    try:
        await bot_message.delete()
        await message.delete()
    except Exception as e:
        message.answer("Cannot delete message!")

async def reply(message: Message, text: str):
    bot_message = await message.answer(text)
    time = db.get_delete_time(message.from_user.id)
    if (time <= 3600):
        scheduler.add_job(delete_message, 
                      trigger='date', 
                      run_date=datetime.now(pytz.utc) + timedelta(seconds=time), 
                      args=(message, bot_message),
                      timezone=pytz.utc)

@dp.message(CommandStart())
async def command_start_handler(message: Message):
    db.add_user(message.from_user.id)
    await reply(message, "Welcome to DnD Dice Roller Bot! Use /help to see all commands.")

async def roll_pattern(message: Message, command: CommandObject, line_prefix: str, func):
    try:
        dices = get_dices(command.args)
        text = ""
        total_sum = 0
        for dice, count in dices:
            if count > 100 or dice > 100 or dice <= 0:
                await reply(message, "Go fuck yourself ❤️")
                return

            result = [func(dice) for i in range(count)]
            print(f"result is {result}")
            text += f"{line_prefix}{count}d{dice}: {", ".join(list(map(str, result)))} = {sum(result)}\n"
            total_sum += sum(result)

        if len(dices) != 1:
            text += "_____________________________________\n"
            text += f"Total sum = {total_sum}"
        await reply(message, text)
    except Exception as e:
        await reply(message, f"An error occurred. Please make sure you provided the details in the correct format")

@dp.message(Command("roll"))
async def roll_handler(message: Message, command: CommandObject):
    await roll_pattern(message, command, "", lambda dice: randint(1, dice))

@dp.message(Command("roll_a"))
async def roll_a_handler(message: Message, command: CommandObject):
    await roll_pattern(message, command, "max ", lambda dice: max(randint(1, dice), randint(1, dice)))

@dp.message(Command("roll_d"))
async def roll_d_handler(message: Message, command: CommandObject):
    await roll_pattern(message, command, "min ", lambda dice: min(randint(1, dice), randint(1, dice)))

@dp.message(Command("set_delete_time"))
async def set_delete_time_handler(message: Message, command: CommandObject):
    try:
        time = int(command.args)
        db.set_delete_time(message.from_user.id, time)
    except Exception as e:
        await reply(message, "An error occurred. Please make sure you provided the details in the correct format")

@dp.message()
async def main():
    scheduler.start() 
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
