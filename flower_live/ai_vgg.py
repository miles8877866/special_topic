import numpy as np
import cv2
import io
# from flask_sqlalchemy import SQLAlchemy
from flask import *
######################
from build_model import model
######################
from PIL import Image
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import pymysql
from sqlalchemy import create_engine


#create_engine用來連接sql的url，
#engine用connect進行連線，
engine = create_engine("mysql+pymysql://root:cvmle814@localhost:3306/flowerlive")
cnx = engine.connect()
# 指定要查詢的路徑
directory = 'static/images/flowerImg/'
allFilePath = ['0.png'] * 101

def preprocess_image(image, target):
    if(image.shape[2] != 3):  ### ch只有一
      image = np.tile(image, (1,1,3))
    image = cv2.resize(image, target, interpolation=cv2.INTER_AREA)
    
    # 將圖片轉為 RGB 模式方便 predict
    # if image.mode != 'RGB':
    #     image = image.convert('RGB')

    # 將資料進行前處理轉成 model 可以使用的 input
    # image=image.resize(target,Image.ANTIALIAS)  
    # #image = image.resize(target)
    # image = img_to_array(image)
    # image=np.array(image,dtype=np.uint8) 
    # # image = np.expand_dims(image, axis=0)
    # # image = imagenet_utils.preprocess_input(image)

    return image

def predict_image_with_path(file_path):
        data = {}
        porb = 0 #機率
        print('request')
        try:
            im = Image.open(file_path)
            
            im = im.resize((64, 64))  # resize the image
            im = np.array(im)  # convert to an array

            # with self.graph.as_default():
            test_image = np.reshape(im, [1, 64, 64, 3 ])
            # reshape it to our input placeholder shape
            p_ = model.predict([test_image])

            # 原本初始化的 tensorflow graph 搭配 sesstion context，預測結果
            temp=0
            image_1 =[]
            image_1.append(im)
            image_1=np.array(image_1)
            preds = model.predict(image_1)
            top_k=3#除了最大的以外，後3個相似的 
            top_k_idx=preds[0].argsort()[::-1][1:top_k]#用np.argsort 然後將其倒過來 1至top_k
            print(top_k_idx)
            for x in p_:
                  for i in range(101):
                    if x[i]>0.8:
                        prob = x[i]
                        x[i]=1
                        temp=i 
                        print(i)
                    else:
                        x[i]=0

            sql = "SELECT * FROM flowerlive.flower_species WHERE id = " + str(temp)
            filepath = "static/images/flowerImg/" + str(temp) + ".jpg"
            conn = engine.connect().connection
            dataframe = pd.read_sql(sql, conn)
            print(filepath)
            print(dataframe)
            
            # 將預測結果整理後回傳 json 檔案（分類和可能機率）
            # for (_, label, prob) in results[0]:
            
            name = dataframe['name'][0]
            nickName = dataframe['nickname'][0]
            sciName = dataframe['scientific_name'][0]
            trait = dataframe['traits'][0]
            use = dataframe['use'][0]
            link = dataframe['link'][0]
            data['filepath'] = filepath
            #data['name'] = str(query_data.fetchone()[1])
            # print('predict numer: {}'.format(p_))
            return ("這是 ~%s~ 的機率有 %.2f%%\n別名 : %s\n學名 : %s\n特徵 : %s\n用途 : %s\n連結 : %s"
             %(name, prob*100, nickName, sciName, trait, use, link))
            # return '我覺得是 label{}!'.format(temp)
        except Exception as e:
            print(e)
            return '哎呀呀辨識不出來內...'