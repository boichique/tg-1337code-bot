import pymysql
import config
import sqlQueries
import datetime
from main import bot


def connect_to_db():
    return pymysql.connect(host=config.host,
                           user=config.user,
                           passwd=config.passwd,
                           database=config.database)


async def send_message():
    report_daily_stat = []
    my_conn = connect_to_db()
    with my_conn:
        with my_conn.cursor() as cursor:
            sql = sqlQueries.stat
            cursor.execute(sql)
    for row in cursor:
        report_daily_stat.append(f"{row[0]} - {row[1] + row[2] + row[3]} ({row[1]} easy {row[2]} medium {row[3]} hard)")
    today = datetime.date.today()
    message = await bot.send_message(config.CHAT_ID, "Статистика на " + today.strftime('%d/%m') + ":\n\n" + "\n".join(report_daily_stat))
    return message.message_id
