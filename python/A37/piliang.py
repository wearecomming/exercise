from model import User,app,db,Record,ImageFile
from  sqlalchemy.sql.expression import func
from flask import Flask,request,jsonify
from flask import Blueprint
from sqlalchemy import desc 
import calendar
from sqlalchemy import or_
import cv2
import math
from datetime import datetime
from sqlalchemy import and_
from datetime import date,timedelta
from sqlalchemy import extract
import jieba
import pandas as pd
import numpy as np
import random
import fasttext

# 加载模型
model = fasttext.load_model('model.bin')

piliang_api = Blueprint('piliang_app', __name__)
def change(text):
    if text=="__label__休闲零食":return "餐饮"
    if text=="__label__娱乐玩具":return "娱乐"
    if text=="__label__文化用品":return "文化教育"
    if text=="__label__办公用品":return "办公"
    if text=="__label__运动用品":return "运动"
    if text=="__label__服装":return "服装"
    if text=="__label__医药":return "医疗"
    if text=="__label__百货用品":return "购物"
    if text=="__label__宠物":return "宠物"
    if text=="__label__家电家装":return "家具"

@app.route('/input_piliang/', methods=['POST'])
def input_piliang():
    user_id=request.form.get("user_id")
    if User.query.get(user_id) is None:
        return jsonify({'status':404 , 'message': '没有'})
    file = request.files.get('file')
    data = pd.read_excel(file)
    l=data.shape[0]
    allx=[]
    for i in range(0,l):
        t=data.iloc[i,0]
        t=t.split(" ")
        if len(t)>2:continue
        date=t[0]
        xx=date.split("-")
        if len(xx)!=3:continue
        time=None
        if xx[1].isdigit()==False or xx[2].isdigit==False:continue
        if len(xx[1])==0 or len(xx[2])==0:continue
        if len(xx[0])<4:continue
        if (int)(xx[1])<=0 or (int)(xx[2])<=0:continue
        if (int)(xx[1])>12 or (int)(xx[2])>28:continue
        if len(t)>1:
            time=t[1]
        froms=data.iloc[i,1]
        if len(froms)>20:continue
        type1=data.iloc[i,2]
        bill=data.iloc[i,3]
        money=data.iloc[i,4]
        value=data.iloc[i,5]
        text=value.replace("/\/", " ")
        label = model.predict(text)
        label=change(label[0][0])
        type2x=label
        dt=datetime.strptime(date,'%Y-%m-%d')
        new_record=Record(type1=type1,type2=type2x,bill=bill,date=date,money=money,froms=froms,value=value,user_id=user_id,datt=dt,tim=time)
        allx.append(new_record)
    db.session.bulk_save_objects(allx)
    db.session.commit()
    return jsonify({'status': 200, 'message': '成功'})
