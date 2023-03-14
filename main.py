from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ContentType
from config import TOKEN_API
import re
import cryptography
import funcs as f
import clases as c


bot = Bot(TOKEN_API)
dp = Dispatcher(bot)

@dp.message_handler(commands = ['stat'])
async def printStat(message: types.Message):
    rows = []
    my_conn = f.connectToDB()
    with my_conn:
        with my_conn.cursor() as cursor:
            sql = """SELECT level, GROUP_CONCAT(DISTINCT name separator \' \') AS name, COUNT(id) AS count 
                    FROM tgChallengeBot.reports 
                    WHERE DATE(date) = CURDATE() 
                    GROUP BY id, level
                    ORDER BY id DESC"""
            cursor.execute(sql)
    for row in cursor:
        f.addInReportArrayLevels(row, rows)

    # my_conn = f.connectToDB()
    # with my_conn:
    #     with my_conn.cursor() as cursor:
    #         sql = """SELECT level, GROUP_CONCAT(DISTINCT name separator \' \') AS name, COUNT(id) AS count
    #                 FROM tgChallengeBot.reports
    #                 WHERE DATE(date) = CURDATE()
    #                 GROUP BY id, level
    #                 ORDER BY id"""
    #         cursor.execute(sql)                    общая сумма задач за сегодня

    if len(rows) > 0:
        await message.answer("Решенные задачи за сегодня:\n" + "\n".join(rows))
    else:
        await message.answer(f'Сегодня не было решено ни одной задачи')


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
        if mess.lower() in ['easy', 'medium', 'hard']:
            level = mess.lower()
        elif 'leetcode.com/problems' in mess:
            link = mess.lower()
        elif re.match('\w+', mess):
            description += mess + ' '
    if len(level) > 0 and len(link) > 0:
        if message.from_user.username:
            username = message.from_user.username
        else:
            username = message.from_user.first_name
        info = c.TaskReport(message.from_user.id, username, message.date, level, link, description)
        my_conn = f.connectToDB()
        with my_conn:
            with my_conn.cursor() as cursor:
                sql = """INSERT INTO reports (`id`, `name`, `date`, `level`, `link`, `description`) 
                        VALUES (%s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (info.id,
                                     info.userName,
                                     info.date.strftime('%Y-%m-%d %H:%M:%S'),
                                     info.level,
                                     info.link,
                                     info.description))
                my_conn.commit()
        await message.answer('Запись о задаче была сохранена.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates = True)