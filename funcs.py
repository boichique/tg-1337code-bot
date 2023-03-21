import pymysql
import config
import queries
import datetime
from bs4 import BeautifulSoup
import requests
import json
import re

from main import bot
from classes import TaskReport


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


def get_daily_challenge():
    query = queries.graphql
    json_data = json.loads(requests.post('https://leetcode.com/graphql/', json={'query': query}).text)
    soup = BeautifulSoup(json_data['data']['activeDailyCodingChallengeQuestion']['question']['content'], 'html.parser')
    disc = soup.text.replace("Constraints:\n", "Constraints:")
    difficulty = json_data["data"]["activeDailyCodingChallengeQuestion"]["question"]["difficulty"]
    title = json_data["data"]["activeDailyCodingChallengeQuestion"]["question"]["title"]
    link = "https://leetcode.com" + json_data["data"]["activeDailyCodingChallengeQuestion"]["link"]
    text=(f"""Дейлик на {datetime.today().strftime("%d/%m/%Y")}
------
*{difficulty}* : [{title}]({link})
------
*Описание*:
```
{disc}
```""")
    return text


def report_on_demand(day1, day2, query):
    report = []
    my_conn = connect_to_db()
    with my_conn:
        with my_conn.cursor() as cursor:
            sql = query
            cursor.execute(sql)
    for row in cursor:
        if (row[1] + row[2] + row[3]) < 2:
            report.append(f"{row[0]} - {row[1] + row[2] + row[3]} ({row[1]} easy {row[2]} medium {row[3]} hard) А ГДЕ??")
        else:
            report.append(f"{row[0]} - {row[1] + row[2] + row[3]} ({row[1]} easy {row[2]} medium {row[3]} hard)")
    if len(report) > 0:
        text = "Решенные задачи за " + day1 + ":\n\n" + "\n".join(report)
    else:
        text = day2 + " не было решено ни одной задачи"
    return text


async def insert_report_into_table(message):
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
        info = TaskReport(message.from_user.id, username, message.date, level, link, description)
        my_conn = connect_to_db()
        with my_conn:
            with my_conn.cursor() as cursor:
                sql = queries.insert
                cursor.execute(sql, (info.id,
                                     info.username,
                                     info.date.strftime('%Y-%m-%d %H:%M:%S'),
                                     info.level,
                                     info.link,
                                     info.description))
                my_conn.commit()
        await bot.send_message(config.REPORT_CHAT_ID, "Запись о задаче была сохранена.")
