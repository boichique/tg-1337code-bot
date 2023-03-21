from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ContentType
from aiogram.utils import executor
from bs4 import BeautifulSoup
import asyncio
import re
import cryptography
import requests
import json
import datetime

import config
import queries
import funcs
import clases


bot = Bot(config.TOKEN_API)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=["help"])
async def print_help(message: types.Message):
    await message.answer("Доступные команды:\n\n" +
                         "/stat - вывод статистики за все время челленджа\n" +
                         "/daily - вывод сегодняшнего дейлика\n" +
                         "/today - вывод статистики по челленджу за сегодня\n" +
                         "/yesterday - вывод статистики по челленджу за вчера\n" +
                         "/week - вывод статистики по челленджу за неделю")


@dp.message_handler(commands=["stat"])
async def print_stat(message: types.Message):
    funcs.motivating_report(message, "все время", "За все время")


@dp.message_handler(commands=["today"])
async def print_today_stat(message: types.Message):
    funcs.motivating_report(message, "сегодня", "Сегодня")


@dp.message_handler(commands=["yesterday"])
async def print_yesterday_stat(message: types.Message):
    funcs.motivating_report(message, "вчера", "Вчера")


@dp.message_handler(commands=["week"])
async def print_week_stat(message: types.Message):
    funcs.motivating_report(message, "неделю", "За эту неделю")


@dp.message_handler(commands=["daily"])
async def send_dailyque(message: types.Message):
    query = queries.graphql
    json_data = json.loads(requests.post("https://leetcode.com/graphql/", json={'query': query}).text)
    soup = BeautifulSoup(json_data['data']['activeDailyCodingChallengeQuestion']['question']['content'], 'html.parser')
    disc = soup.text.replace("Constraints:\n", "Constraints:")
    await message.answer(f"""Дейлик на {datetime.datetime.today().strftime("%d/%m/%Y")}
------
*{json_data["data"]["activeDailyCodingChallengeQuestion"]["question"]["difficulty"]}* : [{json_data["data"]["activeDailyCodingChallengeQuestion"]["question"]["title"]}](https://leetcode.com{json_data["data"]["activeDailyCodingChallengeQuestion"]["link"]})
------
*Описание*:
```
{disc}
```""", parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(commands=["chatId"])                            # Команда для вывода id чата (id нужен для
async def print_chat_id(message: types.Message):                    # отправки сообщений по расписанию)
    await message.answer(f"id этого чата - {message.chat.id}")


@dp.message_handler(content_types=[ContentType.PHOTO, ContentType.TEXT])
async def capture_challenge_report(message: types.Message):
    if message.text is None:
        m = message.caption
    else:
        m = message.text
    level = ""
    link = ""
    description = ""
    for mess in (m.split()):
        if mess.lower() in ["easy", "medium", "hard"]:
            level = mess.lower()
        elif "leetcode.com/problems" in mess:
            link = mess.lower()
        elif re.match("\w+", mess):
            description += mess + " "
    if len(level) > 0 and len(link) > 0:
        if message.from_user.username:
            username = message.from_user.username
        else:
            username = message.from_user.first_name
        info = clases.TaskReport(message.from_user.id, username, message.date, level, link, description)
        my_conn = funcs.connect_to_db()
        with my_conn:
            with my_conn.cursor() as cursor:
                sql = queries.insert
                cursor.execute(sql, (info.id,
                                     info.username,
                                     info.date.strftime("%Y-%m-%d %H:%M:%S"),
                                     info.level,
                                     info.link,
                                     info.description))
                my_conn.commit()
        # await message.answer("Запись о задаче была сохранена.")


async def schedule_messages():
    while True:
        await funcs.send_daily_challenge()                          # Ежедневная отправка дейликов по расписанию
        await asyncio.sleep(43200)
        message_id = await funcs.send_daily_stat()                  # Ежедневная отправка отчетов по расписанию и
        await bot.pin_chat_message(config.CHAT_ID, message_id)      # пин отчета в чате
        await asyncio.sleep(43200)


async def shutdown():                                               # Закрытие сессий бота
    await bot.session.close()
    await dp.storage.close()
    await dp.storage.wait_closed()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(schedule_messages())
    executor.start_polling(dp, skip_updates=True)
    loop.close()
