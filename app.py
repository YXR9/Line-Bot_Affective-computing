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

from connectDB import get_course, update_emotion

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
    course = get_course()
    return render_template("index.html", course=course, userID=userID)

@app.route("/update_study_emotion", methods=['POST'])
def update_study_emotion():
    m_id = request.form['m_id']
    userID = request.form['userID']
    video_time = request.form['video_time']
    emotion = request.form['study_emotion']
    result = 'OK'
    #result = update_emotion(m_id, userID, video_time, emotion)
    # if emotion == "sad":
    #     line_bot_api.push_message(userID, TextSendMessage(text="專心些..."))
    return result

def ptt_hot():
    target_url = 'http://disp.cc/b/PttHot'
    print('Start parsing pttHot....')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""
    for data in soup.select('#list div.row2 div span.listTitle'):
        title = data.text
        link = "http://disp.cc/b/" + data.find('a')['href']
        if data.find('a')['href'] == "796-59l9":
            break
        content += '{}\n{}\n\n'.format(title, link)
    return content

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    userID = event.source.user_id 
    print(event)
    print("event.userID:", userID)
    print("event.reply_token:", event.reply_token)
    print("event.message.texttt:", event.message.text)
    if event.message.text == "學習課程":
        f = open('./static/course_menu.json', 'r', encoding='utf8')
        uri = course_uri + "?userID=" + userID
        text = f.read().format(uri,uri)

        true = True
        content = eval(text)
        line_bot_api.reply_message(reply_token, FlexSendMessage(alt_text='課程選單', contents=content))
        # line_bot_api.reply_message(
        #     event.reply_token,
        #     TextSendMessage(text=content))
    elif event.message.text == "id":
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=userID))
    # if event.message.text == "PTT 表特版 近期大於 10 推的文章":
    #     content = ptt_beauty()
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text=content))
    #     return 0
    # if event.message.text == "來張 imgur 正妹圖片":
    #     client = ImgurClient(client_id, client_secret)
    #     images = client.get_album_images(album_id)
    #     index = random.randint(0, len(images) - 1)
    #     url = images[index].link
    #     image_message = ImageSendMessage(
    #         original_content_url=url,
    #         preview_image_url=url
    #     )
    #     line_bot_api.reply_message(
    #         event.reply_token, image_message)
    #     return 0
    # if event.message.text == "隨便來張正妹圖片":
    #     image = requests.get(API_Get_Image)
    #     url = image.json().get('Url')
    #     image_message = ImageSendMessage(
    #         original_content_url=url,
    #         preview_image_url=url
    #     )
    #     line_bot_api.reply_message(
    #         event.reply_token, image_message)
    #     return 0
    # if event.message.text == "近期熱門廢文":
    #     content = ptt_hot()
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text=content))
    #     return 0
    # if event.message.text == "即時廢文":
    #     content = ptt_gossiping()
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text=content))
    #     return 0
    # if event.message.text == "近期上映電影":
    #     content = movie()
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text=content))
    #     return 0
    # if event.message.text == "觸電網-youtube":
    #     target_url = 'https://www.youtube.com/user/truemovie1/videos'
    #     rs = requests.session()
    #     res = rs.get(target_url, verify=False)
    #     soup = BeautifulSoup(res.text, 'html.parser')
    #     seqs = ['https://www.youtube.com{}'.format(data.find('a')['href']) for data in soup.select('.yt-lockup-title')]
    #     line_bot_api.reply_message(
    #         event.reply_token, [
    #             TextSendMessage(text=seqs[random.randint(0, len(seqs) - 1)]),
    #             TextSendMessage(text=seqs[random.randint(0, len(seqs) - 1)])
    #         ])
    #     return 0
    # if event.message.text == "科技新報":
    #     content = technews()
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text=content))
    #     return 0
    # if event.message.text == "PanX泛科技":
    #     content = panx()
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text=content))
    #     return 0
    # if event.message.text == "開始玩":
    #     buttons_template = TemplateSendMessage(
    #         alt_text='開始玩 template',
    #         template=ButtonsTemplate(
    #             title='選擇服務',
    #             text='請選擇',
    #             thumbnail_image_url='https://i.imgur.com/xQF5dZT.jpg',
    #             actions=[
    #                 MessageTemplateAction(
    #                     label='新聞',
    #                     text='新聞'
    #                 ),
    #                 MessageTemplateAction(
    #                     label='電影',
    #                     text='電影'
    #                 ),
    #                 MessageTemplateAction(
    #                     label='看廢文',
    #                     text='看廢文'
    #                 ),
    #                 MessageTemplateAction(
    #                     label='正妹',
    #                     text='正妹'
    #                 )
    #             ]
    #         )
    #     )
    #     line_bot_api.reply_message(event.reply_token, buttons_template)
    #     return 0
    # if event.message.text == "新聞":
    #     buttons_template = TemplateSendMessage(
    #         alt_text='新聞 template',
    #         template=ButtonsTemplate(
    #             title='新聞類型',
    #             text='請選擇',
    #             thumbnail_image_url='https://i.imgur.com/vkqbLnz.png',
    #             actions=[
    #                 MessageTemplateAction(
    #                     label='蘋果即時新聞',
    #                     text='蘋果即時新聞'
    #                 ),
    #                 MessageTemplateAction(
    #                     label='科技新報',
    #                     text='科技新報'
    #                 ),
    #                 MessageTemplateAction(
    #                     label='PanX泛科技',
    #                     text='PanX泛科技'
    #                 )
    #             ]
    #         )
    #     )
    #     line_bot_api.reply_message(event.reply_token, buttons_template)
    #     return 0
    # if event.message.text == "電影":
    #     buttons_template = TemplateSendMessage(
    #         alt_text='電影 template',
    #         template=ButtonsTemplate(
    #             title='服務類型',
    #             text='請選擇',
    #             thumbnail_image_url='https://i.imgur.com/sbOTJt4.png',
    #             actions=[
    #                 MessageTemplateAction(
    #                     label='近期上映電影',
    #                     text='近期上映電影'
    #                 ),
    #                 MessageTemplateAction(
    #                     label='eyny',
    #                     text='eyny'
    #                 ),
    #                 MessageTemplateAction(
    #                     label='觸電網-youtube',
    #                     text='觸電網-youtube'
    #                 )
    #             ]
    #         )
    #     )
    #     line_bot_api.reply_message(event.reply_token, buttons_template)
    #     return 0
    # if event.message.text == "看廢文":
    #     buttons_template = TemplateSendMessage(
    #         alt_text='看廢文 template',
    #         template=ButtonsTemplate(
    #             title='你媽知道你在看廢文嗎',
    #             text='請選擇',
    #             thumbnail_image_url='https://i.imgur.com/ocmxAdS.jpg',
    #             actions=[
    #                 MessageTemplateAction(
    #                     label='近期熱門廢文',
    #                     text='近期熱門廢文'
    #                 ),
    #                 MessageTemplateAction(
    #                     label='即時廢文',
    #                     text='即時廢文'
    #                 )
    #             ]
    #         )
    #     )
    #     line_bot_api.reply_message(event.reply_token, buttons_template)
    #     return 0
    # if event.message.text == "正妹":
    #     buttons_template = TemplateSendMessage(
    #         alt_text='正妹 template',
    #         template=ButtonsTemplate(
    #             title='選擇服務',
    #             text='請選擇',
    #             thumbnail_image_url='https://i.imgur.com/qKkE2bj.jpg',
    #             actions=[
    #                 MessageTemplateAction(
    #                     label='PTT 表特版 近期大於 10 推的文章',
    #                     text='PTT 表特版 近期大於 10 推的文章'
    #                 ),
    #                 MessageTemplateAction(
    #                     label='來張 imgur 正妹圖片',
    #                     text='來張 imgur 正妹圖片'
    #                 ),
    #                 MessageTemplateAction(
    #                     label='隨便來張正妹圖片',
    #                     text='隨便來張正妹圖片'
    #                 )
    #             ]
    #         )
    #     )
    #     line_bot_api.reply_message(event.reply_token, buttons_template)
    #     return 0
    # if event.message.text == "imgur bot":
    #     carousel_template_message = TemplateSendMessage(
    #         alt_text='ImageCarousel template',
    #         template=ImageCarouselTemplate(
    #             columns=[
    #                 ImageCarouselColumn(
    #                     image_url='https://i.imgur.com/g8zAYMq.jpg',
    #                     action=URIAction(
    #                         label='加我好友試玩',
    #                         uri='https://line.me/R/ti/p/%40gmy1077x'
    #                     ),
    #                 ),
    #             ]
    #         )
    #     )
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         carousel_template_message)
    #     return 0
    # if event.message.text == "油價查詢":
    #     content = oil_price()
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text=content))
    #     return 0

    # carousel_template_message = TemplateSendMessage(
    #     alt_text='目錄 template',
    #     template=CarouselTemplate(
    #         columns=[
    #             CarouselColumn(
    #                 thumbnail_image_url='https://i.imgur.com/kzi5kKy.jpg',
    #                 title='選擇服務',
    #                 text='請選擇',
    #                 actions=[
    #                     MessageAction(
    #                         label='開始玩',
    #                         text='開始玩'
    #                     ),
    #                     URIAction(
    #                         label='影片介紹 阿肥bot',
    #                         uri='https://youtu.be/1IxtWgWxtlE'
    #                     ),
    #                     URIAction(
    #                         label='如何建立自己的 Line Bot',
    #                         uri='https://github.com/twtrubiks/line-bot-tutorial'
    #                     )
    #                 ]
    #             ),
    #             CarouselColumn(
    #                 thumbnail_image_url='https://i.imgur.com/DrsmtKS.jpg',
    #                 title='選擇服務',
    #                 text='請選擇',
    #                 actions=[
    #                     MessageAction(
    #                         label='other bot',
    #                         text='imgur bot'
    #                     ),
    #                     MessageAction(
    #                         label='油價查詢',
    #                         text='油價查詢'
    #                     ),
    #                     URIAction(
    #                         label='聯絡作者',
    #                         uri='https://www.facebook.com/TWTRubiks?ref=bookmarks'
    #                     )
    #                 ]
    #             ),
    #             CarouselColumn(
    #                 thumbnail_image_url='https://i.imgur.com/h4UzRit.jpg',
    #                 title='選擇服務',
    #                 text='請選擇',
    #                 actions=[
    #                     URIAction(
    #                         label='分享 bot',
    #                         uri='https://line.me/R/nv/recommendOA/@vbi2716y'
    #                     ),
    #                     URIAction(
    #                         label='PTT正妹網',
    #                         uri='https://ptt-beauty-infinite-scroll.herokuapp.com/'
    #                     ),
    #                     URIAction(
    #                         label='youtube 程式教學分享頻道',
    #                         uri='https://www.youtube.com/channel/UCPhn2rCqhu0HdktsFjixahA'
    #                     )
    #                 ]
    #             )
    #         ]
    #     )
    # )

    # line_bot_api.reply_message(event.reply_token, carousel_template_message)




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
