import datetime
import math
import os
import psycopg2
import psycopg2.extras
from datetime import datetime, date, timedelta

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

def get_course(m_id):
    try:
        m_id = int(m_id)
    except ValueError:
        print("Oops!  That was no valid number.  Try again...")
        return "None"
    datas = query_db('''select * from "learning_Material" where "id"=%s''',[m_id])
    if datas:
        return datas[0]
    else:
        return "None"
    
def update_emotion(m_id, u_id, video_time, study_emotions):
    insert_or_update('''insert into "learning_emotion" ("m_id", "u_id", "video_time", "study_emotion")
        values (%s, %s, %s, %s)''', [m_id, u_id, video_time, study_emotions])
    return 'OK'