import pymysql
import config

def addInReportArrayLevels(row: [str], m: [[str]]):
    if row[2] == 1:
        m.append(f'{row[1]} решил(-а) {row[2]} задачу уровня - {row[0]}')
    elif row[2] < 5:
        m.append(f'{row[1]} решил(-а) {row[2]} задачи уровня - {row[0]}')
    else:
        m.append(f'{row[1]} решил(-а) {row[2]} задач уровня - {row[0]}')

def addInReportArraySum(row: [str], m: [[str]]):
    if row[2] == 1:
        m.append(f'{row[1]} решил(-а) {row[2]} задачу уровня - {row[0]}')
    elif row[2] < 5:
        m.append(f'{row[1]} решил(-а) {row[2]} задачи уровня - {row[0]}')
    else:
        m.append(f'{row[1]} решил(-а) {row[2]} задач уровня - {row[0]}')
def connectToDB():
    return pymysql.connect(host = config.host,
                            user = config.user,
                            passwd = config.passwd,
                            database = config.database)

