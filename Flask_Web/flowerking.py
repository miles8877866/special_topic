# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 15:19:20 2020

@author: qqwdf
"""
# from keras.preprocessing.image import img_to_array
import numpy as np
import cv2
import io
from flask_sqlalchemy import SQLAlchemy
from flask import *
######################
from build_model import model
######################

db = SQLAlchemy()
# initialize our Flask application and the Keras model
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:cvmle814@localhost:3306/flowerlive"
db.init_app(app)


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

def find_by_name(cls, name):
  return cls.filter_by(name == name).first()

@app.route('/')
def index():
   return render_template('index.html')
   
@app.route('/up_photo', methods = ['GET', 'POST'])
def predict():
    # initialize the data dictionary that will be returned from the
    # view
    data = {'success': False}
    print('request')
    # ensure an image was properly uploaded to our endpoint
    if request.method == 'POST':
        if request.files.get('photo'):
            # 從 flask request 中讀取圖片（byte str）
            image = request.files['photo'].read()
            # 將圖片轉成 PIL 可以使用的格式
            image = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)
            # image = Image.open(io.BytesIO(image))

            # 進行圖片前處理方便預測模型使用
            image = preprocess_image(image, target=(64, 64))
            
            # 原本初始化的 tensorflow graph 搭配 sesstion context，預測結果
            temp=0
            image_1 =[]
            image_1.append(image)
            image_1=np.array(image_1)
            preds = model.predict(image_1)
            for x in preds:
              for i in range(17):
                if x[i]>0.8:
                  x[i]=1
                  temp=i
                  print(i)
                else:
                  x[i]=0
            #results = imagenet_utils.decode_predictions(preds)

            data['predictions'] = []

            # 將預測結果整理後回傳 json 檔案（分類和可能機率）
           # for (_, label, prob) in results[0]:
            r = {'label': temp}#, 'probability': float(prob)}
            data['predictions'].append(r)
            data['success'] = True

    return jsonify(data)
 
@app.route('/test')
def test():
    sql = """
      select *
      from flower_species
    """
    query_data = db.engine.execute(sql)
    result = query_data.fetchone()
    print(result)
    return 'ok'

if __name__ == '__main__':
    app.debug = True
    #load_model()
    app.run()
