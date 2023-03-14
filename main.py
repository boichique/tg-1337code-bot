import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, ContentType
from aiogram.utils import executor, exceptions
from config import TOKEN_API
import sqlQueries
import re
import cryptography
import funcs as f
import clases as c


bot = Bot(TOKEN_API)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=["stat"])
async def print_stat(message: types.Message):
    report_overall = []
    my_conn = f.connect_to_db()
    with my_conn:
        with my_conn.cursor() as cursor:
            sql = sqlQueries.stat
            cursor.execute(sql)
    for row in cursor:
        report_overall.append(f"{row[0]} - {row[1] + row[2] + row[3]} ({row[1]} easy {row[2]} medium {row[3]} hard)")
    await message.answer("Решенные задачи:\n" + "\n".join(report_overall))


@dp.message_handler(commands=["today"])
async def print_today_stat(message: types.Message):
    report_today = []
    my_conn = f.connect_to_db()
    with my_conn:
        with my_conn.cursor() as cursor:
            sql = sqlQueries.today
            cursor.execute(sql)
    for row in cursor:
        if (row[1] + row[2] + row[3]) < 2:
            report_today.append(f"{row[0]} - {row[1] + row[2] + row[3]} ({row[1]} easy {row[2]} medium {row[3]} hard) А ГДЕ??")
        else:
            report_today.append(f"{row[0]} - {row[1] + row[2] + row[3]} ({row[1]} easy {row[2]} medium {row[3]} hard)")
    if len(report_today) > 0:
        await message.answer("Решенные задачи за сегодня:\n" + "\n".join(report_today))
    else:
        await message.answer(f"Сегодня не было решено ни одной задачи")


@dp.message_handler(commands=["yesterday"])
async def print_yesterday_stat(message: types.Message):
    report_yesterday = []
    my_conn = f.connect_to_db()
    with my_conn:
        with my_conn.cursor() as cursor:
            sql = sqlQueries.yesterday
            cursor.execute(sql)
    for row in cursor:
        if (row[1] + row[2] + row[3]) < 2:
            report_yesterday.append(f"{row[0]} - {row[1] + row[2] + row[3]} ({row[1]} easy {row[2]} medium {row[3]} hard) А ГДЕ??")
        else:
            report_yesterday.append(f"{row[0]} - {row[1] + row[2] + row[3]} ({row[1]} easy {row[2]} medium {row[3]} hard)")
    if len(report_yesterday) > 0:
        await message.answer("Решенные задачи за вчера:\n" + "\n".join(report_yesterday))
    else:
        await message.answer(f"Вчера не было решено ни одной задачи")


@dp.message_handler(commands=["week"])
async def print_week_stat(message: types.Message):
    report_week = []
    my_conn = f.connect_to_db()
    with my_conn:
        with my_conn.cursor() as cursor:
            sql = sqlQueries.yesterday
            cursor.execute(sql)
    for row in cursor:
        report_week.append(f"{row[0]} - {row[1] + row[2] + row[3]} ({row[1]} easy {row[2]} medium {row[3]} hard)")
    if len(report_week) > 0:
        await message.answer("Решенные задачи за неделю:\n" + "\n".join(report_week))
    else:
        await message.answer(f"За эту неделю не было решено ни одной задачи")


@dp.message_handler(content_types = [ContentType.PHOTO, ContentType.TEXT])
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
        info = c.TaskReport(message.from_user.id, username, message.date, level, link, description)
        my_conn = f.connect_to_db()
        with my_conn:
            with my_conn.cursor() as cursor:
                sql = sqlQueries.insert
                cursor.execute(sql, (info.id,
                                     info.userName,
                                     info.date.strftime("%Y-%m-%d %H:%M:%S"),
                                     info.level,
                                     info.link,
                                     info.description))
                my_conn.commit()
        await message.answer("Запись о задаче была сохранена.")


# @task.report_daily_task(86400)  # указывается время в секундах (в данном примере - 24 часа).
# async def daily_send():
#     current_time = datetime.datetime.now().strftime("%H:%M:%S")
#     chats = [123456789, 987654321]  # список id чатов, которым нужно отправить сообщение
#     report_daily = []
#     my_conn = f.connect_to_db()
#     with my_conn:
#         with my_conn.cursor() as cursor:
#             sql = sqlQueries.stat
#             cursor.execute(sql)
#     for row in cursor:
#         report_daily.append(f"{row[0]} - {row[1] + row[2] + row[3]} ({row[1]} easy {row[2]} medium {row[3]} hard)")
#     await bot.send_message(msg.from_user.id, msg.text)
# ("Решенные задачи:\n" + "\n".join(report_daily))


# daily_send.start()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates = True)