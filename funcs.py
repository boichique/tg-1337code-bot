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
    await bot.send_message(config.CHAT_ID, f"""Дейлик на {datetime.datetime.today().strftime("%d/%m/%Y")}

Ссылка на задачу: https://leetcode.com{json_data["data"]["activeDailyCodingChallengeQuestion"]["link"]}

Сложность: {json_data["data"]["activeDailyCodingChallengeQuestion"]["question"]["difficulty"]}

Название: {json_data["data"]["activeDailyCodingChallengeQuestion"]["question"]["title"]}


Описание: 
{soup.text}""")

