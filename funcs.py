import pymysql
import config


def connect_to_db():
    return pymysql.connect(host=config.host,
                           user=config.user,
                           passwd=config.passwd,
                           database=config.database)
