import requests
import re
import random
import os
import configparser
from bs4 import BeautifulSoup
from flask import Flask, request, abort, render_template
from imgurpython import ImgurClient


from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import *

from connectDB import *

app = Flask(__name__)
# config = configparser.ConfigParser()


channel_secret = os.getenv('ChannelSecret', None)
channel_access_token = os.getenv('ChannelAccessToken', None)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', None)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

course_uri = "https://project-emotion.herokuapp.com/index"


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@app.route("/video")
def video():
    course = get_course()
    return render_template("video.html", course=course)

@app.route("/index")
def index():
    userID = request.args.get('userID')
    m_id = request.args.get('m_id')
    course = get_course(m_id)
    if course != "None":
        return render_template("index.html", course=course, userID=userID)
    else:
        return "課程不存在"

@app.route("/update_study_emotion", methods=['POST'])
def update_study_emotion():
    m_id = request.form['m_id']
    userID = request.form['userID']
    video_time = request.form['video_time']
    emotion = request.form['study_emotion']
    flag = request.form['flag']
    result = 'OK'
    print("flag is ", flag)
    result = update_emotion(m_id, userID, video_time, emotion)
    if (emotion == "sad" or emotion == "disgusted" or emotion == "angry") and flag == '0':
        emotion_id = get_newest_emotion_id(userID)
        update_video_status(emotion_id, False)
        send_notification(m_id, userID)
        return str(emotion_id)
    else:
        return "0"

@app.route("/check_study_video_status", methods=['POST'])
def check_study_video_status():
    e_id = request.form["e_id"]
    video_status = check_video_status(e_id)
    return str(video_status)

def send_course_keyword(reply_token, m_id):
    keyword = get_keyword(m_id)
    course = get_course(m_id)
    f = open('./static/course_keyword.json', 'r', encoding='utf8')
    neww = ''
    
    for i in range(len(keyword)):
        add_json = []
        new = ''
        if i != (len(keyword)-1):
            add_json.append({"margin": "md","type": "box","layout": "vertical","contents": [{"type": "text","text": "H","color": "#01BCE4","size": "xxs"},
                {"type": "text","text": "{}".format(keyword[i]["keyword"]),"wrap": True,"color": "#FFFFFF","margin": "sm","align": "center","offsetTop": "none","size": "md"},
                {"type": "text","text": "H","color": "#01BCE4","size": "xxs"}],"borderWidth": "light","borderColor": "#01BCE4","justifyContent": "center",
                "background": {"type": "linearGradient","angle": "0deg","startColor": "#01BCE4","endColor": "#01BCE4"},"cornerRadius": "sm","spacing": "none",
                "offsetTop": "none","action": {"type": "postback","label": "action","data": "keyword_id_{}_{}".format(keyword[i]["id"], keyword[i]["m_id"])}})
            # add_json.append({"margin": "md","type": "box","layout": "horizontal","contents": [{"type": "button","action": {"type": "postback","label": "{}".format(keyword[i]["keyword"]),
            #     "data": "keyword_id_{}".format(keyword[i]["id"])},"color": "#FFFFFF","style": "link"}],"background": {"type": "linearGradient","angle": "0deg","startColor": "#01BCE4",
            #     "endColor": "#01BCE4"},"cornerRadius": "sm"})
            new_add = str(add_json[0]) + ","
            print(new_add)
        else:
            add_json.append({"margin": "md","type": "box","layout": "vertical","contents": [{"type": "text","text": "H","color": "#01BCE4","size": "xxs"},
                {"type": "text","text": "{}".format(keyword[i]["keyword"]),"wrap": True,"color": "#FFFFFF","margin": "sm","align": "center","offsetTop": "none","size": "md"},
                {"type": "text","text": "H","color": "#01BCE4","size": "xxs"}],"borderWidth": "light","borderColor": "#01BCE4","justifyContent": "center",
                "background": {"type": "linearGradient","angle": "0deg","startColor": "#01BCE4","endColor": "#01BCE4"},"cornerRadius": "sm","spacing": "none",
                "offsetTop": "none","action": {"type": "postback","label": "action","data": "keyword_id_{}_{}".format(keyword[i]["id"], keyword[i]["m_id"])}})
            # add_json.append({"margin": "md","type": "box","layout": "horizontal","contents": [{"type": "button","action": {"type": "postback","label": "{}".format(keyword[i]["keyword"]),
            #     "data": "keyword_id_{}".format(keyword[i]["id"])},"color": "#FFFFFF","style": "link"}],"background": {"type": "linearGradient","angle": "0deg","startColor": "#01BCE4",
            #     "endColor": "#01BCE4"},"cornerRadius": "sm"})
            new_add = str(add_json[0])
            print(add_json[0])
        neww = str(neww) + str(new_add)
    print("neww is ", neww)
    text = f.read().format(course["courseName"],neww)
    true = True
    content = eval(text)
    line_bot_api.reply_message(reply_token, FlexSendMessage(alt_text='課程keyword', contents=content))

def resend_course_keyword(reply_token, m_id, description):
    keyword = get_keyword(m_id)
    course = get_course(m_id)
    f = open('./static/course_keyword.json', 'r', encoding='utf8')
    neww = ''
    
    for i in range(len(keyword)):
        add_json = []
        new = ''
        if i != (len(keyword)-1):
            add_json.append({"margin": "md","type": "box","layout": "vertical","contents": [{"type": "text","text": "H","color": "#01BCE4","size": "xxs"},
                {"type": "text","text": "{}".format(keyword[i]["keyword"]),"wrap": True,"color": "#FFFFFF","margin": "sm","align": "center","offsetTop": "none","size": "md"},
                {"type": "text","text": "H","color": "#01BCE4","size": "xxs"}],"borderWidth": "light","borderColor": "#01BCE4","justifyContent": "center",
                "background": {"type": "linearGradient","angle": "0deg","startColor": "#01BCE4","endColor": "#01BCE4"},"cornerRadius": "sm","spacing": "none",
                "offsetTop": "none","action": {"type": "postback","label": "action","data": "keyword_id_{}_{}".format(keyword[i]["id"], keyword[i]["m_id"])}})
            # add_json.append({"margin": "md","type": "box","layout": "horizontal","contents": [{"type": "button","action": {"type": "postback","label": "{}".format(keyword[i]["keyword"]),
            #     "data": "keyword_id_{}".format(keyword[i]["id"])},"color": "#FFFFFF","style": "link"}],"background": {"type": "linearGradient","angle": "0deg","startColor": "#01BCE4",
            #     "endColor": "#01BCE4"},"cornerRadius": "sm"})
            new_add = str(add_json[0]) + ","
            print(new_add)
        else:
            add_json.append({"margin": "md","type": "box","layout": "vertical","contents": [{"type": "text","text": "H","color": "#01BCE4","size": "xxs"},
                {"type": "text","text": "{}".format(keyword[i]["keyword"]),"wrap": True,"color": "#FFFFFF","margin": "sm","align": "center","offsetTop": "none","size": "md"},
                {"type": "text","text": "H","color": "#01BCE4","size": "xxs"}],"borderWidth": "light","borderColor": "#01BCE4","justifyContent": "center",
                "background": {"type": "linearGradient","angle": "0deg","startColor": "#01BCE4","endColor": "#01BCE4"},"cornerRadius": "sm","spacing": "none",
                "offsetTop": "none","action": {"type": "postback","label": "action","data": "keyword_id_{}_{}".format(keyword[i]["id"], keyword[i]["m_id"])}})
            # add_json.append({"margin": "md","type": "box","layout": "horizontal","contents": [{"type": "button","action": {"type": "postback","label": "{}".format(keyword[i]["keyword"]),
            #     "data": "keyword_id_{}".format(keyword[i]["id"])},"color": "#FFFFFF","style": "link"}],"background": {"type": "linearGradient","angle": "0deg","startColor": "#01BCE4",
            #     "endColor": "#01BCE4"},"cornerRadius": "sm"})
            new_add = str(add_json[0])
            print(add_json[0])
        neww = str(neww) + str(new_add)
    print("neww is ", neww)
    text = f.read().format(course["courseName"],neww)
    true = True
    content = eval(text)
    line_bot_api.reply_message(reply_token, [TextSendMessage(text=description), FlexSendMessage(alt_text='課程keyword', contents=content)])

def question_send_course_keyword(reply_token, m_id):
    keyword = get_keyword(m_id)
    course = get_course(m_id)
    f = open('./static/course_keyword.json', 'r', encoding='utf8')
    neww = ''
    for i in range(len(keyword)):
        add_json = []
        new = ''
        if i != (len(keyword)-1):
            add_json.append({"margin": "md","type": "box","layout": "vertical","contents": [{"type": "text","text": "H","color": "#01BCE4","size": "xxs"},
                {"type": "text","text": "{}".format(keyword[i]["keyword"]),"wrap": True,"color": "#FFFFFF","margin": "sm","align": "center","offsetTop": "none","size": "md"},
                {"type": "text","text": "H","color": "#01BCE4","size": "xxs"}],"borderWidth": "light","borderColor": "#01BCE4","justifyContent": "center",
                "background": {"type": "linearGradient","angle": "0deg","startColor": "#01BCE4","endColor": "#01BCE4"},"cornerRadius": "sm","spacing": "none",
                "offsetTop": "none","action": {"type": "postback","label": "action","data": "keyword_id_{}_{}".format(keyword[i]["id"], keyword[i]["m_id"])}})
            new_add = str(add_json[0]) + ","
            print(new_add)
        else:
            add_json.append({"margin": "md","type": "box","layout": "vertical","contents": [{"type": "text","text": "H","color": "#01BCE4","size": "xxs"},
                {"type": "text","text": "{}".format(keyword[i]["keyword"]),"wrap": True,"color": "#FFFFFF","margin": "sm","align": "center","offsetTop": "none","size": "md"},
                {"type": "text","text": "H","color": "#01BCE4","size": "xxs"}],"borderWidth": "light","borderColor": "#01BCE4","justifyContent": "center",
                "background": {"type": "linearGradient","angle": "0deg","startColor": "#01BCE4","endColor": "#01BCE4"},"cornerRadius": "sm","spacing": "none",
                "offsetTop": "none","action": {"type": "postback","label": "action","data": "keyword_id_{}_{}".format(keyword[i]["id"], keyword[i]["m_id"])}})
            new_add = str(add_json[0])
            print(add_json[0])
        neww = str(neww) + str(new_add)
    print("neww is ", neww)
    text = f.read().format(course["courseName"],neww)
    true = True
    content = eval(text)
    line_bot_api.reply_message(reply_token, [TextSendMessage(text="答錯囉，請看看是否還有不懂的地方！"),FlexSendMessage(alt_text='課程keyword', contents=content)])

def send_notification(m_id,userID):
    f = open('./static/check_understand.json', 'r', encoding='utf8')
    text = f.read().format(m_id, m_id)
    true = True
    content = eval(text)
    line_bot_api.push_message(userID, [TextSendMessage(text="專心些..."), FlexSendMessage(alt_text='對課程的理解', contents=content)])

def send_course_question(reply_token, m_id, userID):
    question = get_course_question(m_id)
    f = open('./static/course_question.json', 'r', encoding='utf8')
    text = f.read().format(question["quiz"], question["options1"], question["options2"], question["options3"], question["options4"], m_id, m_id, m_id, m_id)
    true = True
    content = eval(text)
    line_bot_api.reply_message(reply_token, [TextSendMessage(text="請回答以下題目"), FlexSendMessage(alt_text='題目', contents=content)])

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    userID = event.source.user_id 
    print(event)
    print("event.userID:", userID)
    print("event.reply_token:", event.reply_token)
    print("event.message.texttt:", event.message.text)
    if event.message.text == "學習課程":
        f = open('./static/course_menu.json', 'r', encoding='utf8')
        uri = course_uri + "?userID=" + userID + "&m_id="
        text = f.read().format(uri + "1",uri + "2")

        true = True
        content = eval(text)
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text='課程選單', contents=content))
    elif event.message.text == "id":
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=userID))
    elif event.message.text[0:7] == "keyword":
        m_id = event.message.text[7:]
        send_course_keyword(event.reply_token, m_id)

@handler.add(PostbackEvent)
def handle_postback(event):
    userID = event.source.user_id
    text = event.postback.data
    stu_video_status = get_student_video_status(userID)
    if stu_video_status != None and stu_video_status == True:
        if text[0:11] == 'keyword_id_':
            info = text[11:]
            info = info.split("_")
            keyword_id = info[0]
            m_id = info[1]
            keyword_result = get_keyword_description(keyword_id)
            text = keyword_result["keyword"] + ":\n" + keyword_result["description"]
            resend_course_keyword(event.reply_token, m_id, text)
        elif text[0:4] == "YES_":
            m_id = text[4:]
            send_course_keyword(event.reply_token, m_id)
        elif text[0:3] == "NO_":
            m_id = text[3:]
            send_course_question(event.reply_token, m_id, userID)
        elif text == "understand_all_keyword":
            e_id = get_newest_emotion_id(userID)
            update_video_status(e_id, True)
        elif text[0:6] == "answer":
            temp = text[6:]
            temp = temp.split("_")
            m_id = temp[0]
            select = temp[1]
            question = get_course_question(m_id)
            e_id = get_newest_emotion_id(userID)
            if select == str(question["answer"]):
                update_video_status(e_id, True)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="答對了，繼續看影片吧！"))
            else:
                question_send_course_keyword(event.reply_token, m_id)
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="同學~請不要玩機器人，專心上課🤨"))
            

@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    print("package_id:", event.message.package_id)
    print("sticker_id:", event.message.sticker_id)
    # ref. https://developers.line.me/media/messaging-api/sticker_list.pdf
    sticker_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 21, 100, 101, 102, 103, 104, 105, 106,
                   107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125,
                   126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 401, 402]
    index_id = random.randint(0, len(sticker_ids) - 1)
    sticker_id = str(sticker_ids[index_id])
    print(index_id)
    sticker_message = StickerSendMessage(
        package_id='1',
        sticker_id=sticker_id
    )
    line_bot_api.reply_message(
        event.reply_token,
        sticker_message)


if __name__ == '__main__':
    app.run()
