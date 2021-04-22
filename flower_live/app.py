from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

import os
import time

# from ai import AI
from message import *
from file import File
import ai_vgg
# SQL
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import pymysql
from sqlalchemy import create_engine
directory = 'static/images/flowerImg/'
allFilePath = ['0.png'] * 101

engine = create_engine("mysql+pymysql://root:cvmle814@localhost:3306/flowerlive")
cnx = engine.connect()
# Channel Access Token
file = open('channel_access_token.txt', encoding='utf8')
text = file.read().strip()
line_bot_api = LineBotApi(text)
file.close()

# Channel Secret
file = open('channel_secret.txt', encoding='utf8')
text = file.read().strip()
handler = WebhookHandler(text)
file.close()

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

user_guess = "NULLLLLLLLLLLLLLLL" #儲存user上次輸入
user_guess_state = 1
# 處理文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global user_guess
    global user_guess_state
    msg = event.message.text  # msg 是使用者發過來的String.
    
    #功能選單
    if '使用說明' in msg:
        message = TextSendMessage(text='功能介紹~\n'\
            '1. 拍照或上傳一張花的圖片\n讓我們來幫你看看是甚麼花!\n\n'\
            '2. 點擊~花花小測驗~\n會隨機出現一種花\n考考你的花花小知識~\n\n'\
            '3. 點擊~每日花語~\n會出現一種今日幸運花朵\n運氣夠好的話\n你將會被幸運花花造訪>o<\n\n'\
            '4. 點擊~淡江花庫~\n可以看到<花現生活>目前能辨認那些花朵\n那我們也會持續增加喔^^\n\n'\
            '5. 使用@花名\n可以查看該花卉的相關資料喔!\n\n'
            ' 讓我們一起花現生活的美好吧!!')
        line_bot_api.reply_message(event.reply_token, message)
    #選擇題
    elif '花花小測驗' in msg:
        message, guess = buttons_message() #輸出的猜測句子
        user_guess = guess
        user_guess_state = 1
        line_bot_api.reply_message(event.reply_token, message)
    #每日花語
    elif '每日花語' in msg:
        today = time.strftime ( "%#m月%#d日" , time.localtime ()) #加#號不補0
        sql = "SELECT * FROM flowerlive.flower_meaning WHERE date = " + "\"" + today + "\""
        conn = engine.connect().connection
        dataframe = pd.read_sql(sql, conn)
        date = dataframe['date'][0]
        name = dataframe['name'][0]
        sentence = dataframe['sentence'][0]
        message = TextSendMessage(text='今天日期 : %s\n幸運花是 ~%s~\n花語 : %s' %(date, name, sentence))
        line_bot_api.reply_message(event.reply_token, message)
    #花庫
    elif '淡江花庫' in msg:
        sql = "SELECT * FROM flowerlive.flower_species where scientific_name != '' and scientific_name is not null"
        conn = engine.connect().connection
        dataframe = pd.read_sql(sql, conn)
        # dataframe = dataframe.values()
        #回傳淡江花庫的字串
        return_str = ''
        for i in range(1, len(dataframe)):
            return_str = return_str + ("No.%d %s\n" %(i, dataframe['name'][i])) 
        print(return_str)
        message = TextSendMessage(text = '目前我們有以下這些花\n%s\n那我們後續還會再增加呦~敬請期待' %return_str)
        line_bot_api.reply_message(event.reply_token, message)
    #處理選擇題問答
    elif msg == user_guess and user_guess_state == 1:
        sql = "SELECT * FROM flowerlive.flower_species WHERE name = " + "\"" + user_guess + "\""
        conn = engine.connect().connection
        dataframe = pd.read_sql(sql, conn)
        name = dataframe['name'][0]
        nickName = dataframe['nickname'][0]
        sciName = dataframe['scientific_name'][0]
        trait = dataframe['traits'][0]
        use = dataframe['use'][0]
        link = dataframe['link'][0]
        
        message = TextSendMessage("哇!恭喜你答對囉~\n看來你是真的花花小達人呢!\n" \
            + "以下是此花相關資訊喔!\n" \
            + "名稱 : %s\n別名 : %s\n學名 : %s\n特徵 : %s\n用途 : %s\n連結 : %s"
            %(name, nickName, sciName, trait, use, link))
        user_guess_state = 0
        print("user state %d" %user_guess_state)
        line_bot_api.reply_message(event.reply_token, message)
    elif msg != user_guess and user_guess_state == 1:
        sql = "SELECT * FROM flowerlive.flower_species WHERE name = " + "\"" + user_guess + "\""
        conn = engine.connect().connection
        dataframe = pd.read_sql(sql, conn)
        name = dataframe['name'][0]
        nickName = dataframe['nickname'][0]
        sciName = dataframe['scientific_name'][0]
        trait = dataframe['traits'][0]
        use = dataframe['use'][0]
        link = dataframe['link'][0]

        message = TextSendMessage("好可惜呢!再多多嘗試吧\n相信你終有一天會成為花花小達人的!\n" \
            + "以下是此花相關資訊喔!\n" \
            + "名稱 : %s\n別名 : %s\n學名 : %s\n特徵 : %s\n用途 : %s\n連結 : %s"
            %(name, nickName, sciName, trait, use, link))
        
        user_guess_state = 0
        print("user state %d" %user_guess_state)
        line_bot_api.reply_message(event.reply_token, message)
    #處理查詢
    elif '@' in msg:
        print("%s" %(msg[1:]))
        sql = "SELECT * FROM flowerlive.flower_species WHERE name = " + "\"" + (msg[1:]) + "\""
        conn = engine.connect().connection
        dataframe = pd.read_sql(sql, conn)
        print(dataframe)
        if dataframe.shape[0] != 0: #判斷dataframe，若有返回值，則有此花
            name = dataframe['name'][0]
            nickName = dataframe['nickname'][0]
            sciName = dataframe['scientific_name'][0]
            trait = dataframe['traits'][0]
            use = dataframe['use'][0]
            link = dataframe['link'][0]
            # photo = ImageSendMessage(original_content_url=filepath)
            message = TextSendMessage(text="名稱 : %s\n別名 : %s\n學名 : %s\n特徵 : %s\n用途 : %s\n連結 : %s"
                %(name, nickName, sciName, trait, use, link))
        
            line_bot_api.reply_message(event.reply_token, message)
        else:
            message = TextSendMessage(text="圖庫中沒有這種花喔!!\n檢查一下是不是打錯字呢?")
            line_bot_api.reply_message(event.reply_token, message)
    else:  
        message = TextSendMessage(text='阿內母湯喔~\n傳給我一朵花的照片啦!\n讓我看看是什麼花！')
        line_bot_api.reply_message(event.reply_token, message)
    print('-----------------')

# 處理影音訊息
@handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
def handle_content_message(event):
    is_image = False
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
        is_image = True
    elif isinstance(event.message, VideoMessage):
        ext = 'mp4'
    elif isinstance(event.message, AudioMessage):
        ext = 'm4a'
    else:
        is_image == False

    if is_image == False:
        line_bot_api.reply_message(event.reply_token, '這好像不是圖片唷')
    else:
        message_content = line_bot_api.get_message_content(event.message.id)
        img, file_path = file.save_bytes_image(message_content.content)
        pred = ai_vgg.predict_image_with_path(file_path)

        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text=pred)
            ])

# ai = AI()
file = File()

if __name__ == "__main__":
    app.debug = True
    # port = int(os.environ.get('PORT', 5000))
    # app.run(host='0.0.0.0', port=port)
    app.run()   #host='0.0.0.0', port=port