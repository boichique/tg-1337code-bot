import pymysql
import config

def connectToDB():
    return pymysql.connect(host = config.host,
                            user = config.user,
                            passwd = config.passwd,
                            database = config.database)

