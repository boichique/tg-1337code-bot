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
import markdownify

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
    report_overall = []
    my_conn = funcs.connect_to_db()
    with my_conn:
        with my_conn.cursor() as cursor:
            sql = queries.stat
            cursor.execute(sql)
    for row in cursor:
        report_overall.append(f"{row[0]} - {row[1] + row[2] + row[3]} ({row[1]} easy {row[2]} medium {row[3]} hard)")
    await message.answer("Решенные задачи:\n\n" + "\n".join(report_overall))


@dp.message_handler(commands=["today"])
async def print_today_stat(message: types.Message):
    report_today = []
    my_conn = funcs.connect_to_db()
    with my_conn:
        with my_conn.cursor() as cursor:
            sql = queries.today
            cursor.execute(sql)
    for row in cursor:
        if (row[1] + row[2] + row[3]) < 2:
            report_today.append(f"{row[0]} - {row[1] + row[2] + row[3]} ({row[1]} easy {row[2]} medium {row[3]} hard) А ГДЕ??")
        else:
            report_today.append(f"{row[0]} - {row[1] + row[2] + row[3]} ({row[1]} easy {row[2]} medium {row[3]} hard)")
    if len(report_today) > 0:
        await message.answer("Решенные задачи за сегодня:\n\n" + "\n".join(report_today))
    else:
        await message.answer(f"Сегодня не было решено ни одной задачи")


@dp.message_handler(commands=["yesterday"])
async def print_yesterday_stat(message: types.Message):
    report_yesterday = []
    my_conn = funcs.connect_to_db()
    with my_conn:
        with my_conn.cursor() as cursor:
            sql = queries.yesterday
            cursor.execute(sql)
    for row in cursor:
        if (row[1] + row[2] + row[3]) < 2:
            report_yesterday.append(f"{row[0]} - {row[1] + row[2] + row[3]} ({row[1]} easy {row[2]} medium {row[3]} hard) А ГДЕ??")
        else:
            report_yesterday.append(f"{row[0]} - {row[1] + row[2] + row[3]} ({row[1]} easy {row[2]} medium {row[3]} hard)")
    if len(report_yesterday) > 0:
        await message.answer("Решенные задачи за вчера:\n\n" + "\n".join(report_yesterday))
    else:
        await message.answer(f"Вчера не было решено ни одной задачи")


@dp.message_handler(commands=["week"])
async def print_week_stat(message: types.Message):
    report_week = []
    my_conn = funcs.connect_to_db()
    with my_conn:
        with my_conn.cursor() as cursor:
            sql = queries.week
            cursor.execute(sql)
    for row in cursor:
        report_week.append(f"{row[0]} - {row[1] + row[2] + row[3]} ({row[1]} easy {row[2]} medium {row[3]} hard)")
    if len(report_week) > 0:
        await message.answer("Решенные задачи за неделю:\n\n" + "\n".join(report_week))
    else:
        await message.answer(f"За эту неделю не было решено ни одной задачи")


@dp.message_handler(commands=["daily"])
async def send_dailyque(message: types.Message):
    query = queries.graphql
    json_data = json.loads(requests.post("https://leetcode.com/graphql/", json={'query': query}).text)
    soup = BeautifulSoup(json_data["data"]["activeDailyCodingChallengeQuestion"]["question"]["content"], "html5lib")
    await message.answer(f"""Дейлик на {datetime.datetime.today().strftime("%d/%m/%Y")}

Ссылка на задачу: https://leetcode.com{json_data["data"]["activeDailyCodingChallengeQuestion"]["link"]}

Сложность: {json_data["data"]["activeDailyCodingChallengeQuestion"]["question"]["difficulty"]}

Название: {json_data["data"]["activeDailyCodingChallengeQuestion"]["question"]["title"]}


Описание: 
{soup.text}""")


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
        await message.answer("Запись о задаче была сохранена.")


async def schedule_messages():
    while True:
        message_id = await funcs.send_daily_stat()                  # Ежедневная отправка отчетов по расписанию и
        await bot.pin_chat_message(config.CHAT_ID, message_id)      # пин отчета в чате
        await asyncio.sleep(43200)
        await funcs.send_daily_challenge()                          # Ежедневная отправка дейликов по расписанию
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
