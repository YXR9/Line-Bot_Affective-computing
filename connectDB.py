import datetime
import math
import os
import psycopg2
import psycopg2.extras
from datetime import datetime, date, timedelta
import bcrypt

DATABASE_URL = os.environ['DATABASE_URL']


def query_db(query, args=(), one=False):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute(query, args)
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    datas = []
    for r in rows:
        data = dict()
        for i in range(len(cursor.description)):
            data[cursor.description[i][0]] = r[i]
        datas.append(data)
    return datas


def insert_or_update(query, args=(), one=False):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    cursor.execute(query, args)
    conn.commit()
    conn.close()
    return 'insert or update data'

def get_course():
    datas = query_db('''select * from learning_Material ORDER BY "id" limit 1''')
    return datas[0]