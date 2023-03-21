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


def get_daily_challenge():
    query = queries.graphql
    json_data = json.loads(requests.post('https://leetcode.com/graphql/', json={'query': query}).text)
    soup = BeautifulSoup(json_data['data']['activeDailyCodingChallengeQuestion']['question']['content'], 'html.parser')
    disc = soup.text.replace("Constraints:\n", "Constraints:")
    difficulty = json_data["data"]["activeDailyCodingChallengeQuestion"]["question"]["difficulty"]
    title = json_data["data"]["activeDailyCodingChallengeQuestion"]["question"]["title"]
    link = "https://leetcode.com" + json_data["data"]["activeDailyCodingChallengeQuestion"]["link"]
    text=(f"""Дейлик на {datetime.datetime.today().strftime("%d/%m/%Y")}
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
