from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ContentType
from config import TOKEN_API
import sqlQueries
import re
import cryptography
import funcs as f
import clases as c


bot = Bot(TOKEN_API)
dp = Dispatcher(bot)


@dp.message_handler(commands = ["stat"])
async def printStat(message: types.Message):
    reportOverall = []
    my_conn = f.connectToDB()
    with my_conn:
        with my_conn.cursor() as cursor:
            sql = sqlQueries.stat
            cursor.execute(sql)
    for row in cursor:
        if (row[1] + row[2] + row[3]) < 2:
            reportOverall.append(f"{row[0]} - {row[1]+row[2]+row[3]} ({row[1]} easy {row[2]} medium {row[3]} hard) А ГДЕ??")
        else:
            reportOverall.append(f"{row[0]} - {row[1] + row[2] + row[3]} ({row[1]} easy {row[2]} medium {row[3]} hard)")
    await message.answer("Решенные задачи:\n" + "\n".join(reportOverall))
@dp.message_handler(commands = ["today"])
async def printTodayStat(message: types.Message):
    reportToday = []
    my_conn = f.connectToDB()
    with my_conn:
        with my_conn.cursor() as cursor:
            sql = sqlQueries.today
            cursor.execute(sql)
    for row in cursor:
        if (row[1] + row[2] + row[3]) < 2:
            reportToday.append(
                f"{row[0]} - {row[1] + row[2] + row[3]} ({row[1]} easy {row[2]} medium {row[3]} hard) А ГДЕ??")
        else:
            reportToday.append(f"{row[0]} - {row[1] + row[2] + row[3]} ({row[1]} easy {row[2]} medium {row[3]} hard)")
    if len(reportToday) > 0:
        await message.answer("Решенные задачи за сегодня:\n" + "\n".join(reportToday))
    else:
        await message.answer(f"Сегодня не было решено ни одной задачи")
@dp.message_handler(content_types = [ContentType.PHOTO, ContentType.TEXT])
async def captureChallengeReport(message: types.Message):
    if message.text is None:
        m = message.caption
    else:
        m = message.text
    level = ''
    link = ''
    description = ''
    for mess in (m.split()):
        if mess.lower() in ["easy", "medium", "hard"]:
            level = mess.lower()
        elif "leetcode.com/problems" in mess:
            link = mess.lower()
        elif re.match('\w+', mess):
            description += mess + " "
    if len(level) > 0 and len(link) > 0:
        if message.from_user.username:
            username = message.from_user.username
        else:
            username = message.from_user.first_name
        info = c.TaskReport(message.from_user.id, username, message.date, level, link, description)
        my_conn = f.connectToDB()
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


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates = True)