#這些是LINE官方開放的套件組合透過import來套用這個檔案上
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
# SQL
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import pymysql
from sqlalchemy import create_engine
#隨機亂數
import random 

directory = 'static/images/flowerImg/'
allFilePath = ['0.png'] * 101
engine = create_engine("mysql+pymysql://root:cvmle814@localhost:3306/flowerlive")
cnx = engine.connect()


#TemplateSendMessage - ButtonsTemplate (按鈕介面訊息)
def buttons_message():
    sql = "SELECT id, name, image_href FROM flowerlive.flower_href WHERE image_href is not null \
            order by rand() limit 4"
    conn = engine.connect().connection
    dataframe = pd.read_sql(sql, conn)
    print(dataframe)
    
    index =  random.randint(0, 3) #0-3取一個數當作index，use random function
    print(index)
    message = TemplateSendMessage(
        alt_text = '隨機出題中~~',
        template = ButtonsTemplate(
            thumbnail_image_url = dataframe['image_href'][index],
            title="你認得這是甚麼花嗎?",
            text="注意!只有一次選擇機會喔!",
            actions=[
                MessageTemplateAction(
                    label = dataframe['name'][0],
                    text = "%s" %dataframe['name'][0]
                ),
                MessageTemplateAction(
                    label = dataframe['name'][1],
                    text = "%s" %dataframe['name'][1]
                ),
                MessageTemplateAction(
                    label = dataframe['name'][2],
                    text = "%s" %dataframe['name'][2]
                ),
                MessageTemplateAction(
                    label = dataframe['name'][3],
                    text = "%s" %dataframe['name'][3]
                )
            ]
        )
    )
    
    return message, dataframe['name'][index]
    