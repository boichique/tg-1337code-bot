import pymysql
import config
import queries
import datetime
from bs4 import BeautifulSoup
import requests
import json

from main import bot


def connect_to_db():
    return pymysql.connect(host=config.host,
                           user=config.user,
                           passwd=config.passwd,
                           database=config.database)


async def send_daily_stat():
    report_daily_stat = []
    my_conn = connect_to_db()
    with my_conn:
        with my_conn.cursor() as cursor:
            sql = queries.stat
            cursor.execute(sql)
    for row in cursor:
        report_daily_stat.append(f"{row[0]} - {row[1] + row[2] + row[3]} ({row[1]} easy {row[2]} medium {row[3]} hard)")
    today = datetime.date.today()
    message = await bot.send_message(config.CHAT_ID, "Статистика на " + today.strftime('%d/%m') + ":\n\n" + "\n".join(report_daily_stat))
    return message.message_id


async def send_daily_challenge():
    query = queries.graphql
    json_data = json.loads(requests.post('https://leetcode.com/graphql/', json={'query': query}).text)
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


def motivating_report(message, day1, day2):
    report = []
    my_conn = connect_to_db()
    with my_conn:
        with my_conn.cursor() as cursor:
            sql = queries.yesterday
            cursor.execute(sql)
    for row in cursor:
        if (row[1] + row[2] + row[3]) < 2:
            report.append(f"{row[0]} - {row[1] + row[2] + row[3]} ({row[1]} easy {row[2]} medium {row[3]} hard) А ГДЕ??")
        else:
            report.append(f"{row[0]} - {row[1] + row[2] + row[3]} ({row[1]} easy {row[2]} medium {row[3]} hard)")
    if len(report) > 0:
        await message.answer("Решенные задачи за " + day1 + ":\n\n" + "\n".join(report))
    else:
        await message.answer(day2 + " не было решено ни одной задачи")
