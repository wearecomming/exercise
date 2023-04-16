from sdk import get_sdk
from model import User,app,db,Record,ImageFile
from  sqlalchemy.sql.expression import func
from flask import Flask,request,jsonify
from flask import Blueprint
from sqlalchemy import desc 
import calendar
import os
import subprocess
from sqlalchemy import or_
import cv2
import math
from datetime import datetime
from sqlalchemy import and_
import random
from datetime import date,timedelta
from sqlalchemy import extract
import numpy as np
import http.client
import json
yuyin_api = Blueprint('yuyin_app', __name__)
def process(request, token, audioFile) :

    # -*- coding: UTF-8 -*-
# Python 2.x引入httplib模块
# import httplib
# Python 3.x引入http.client模块
    # 读取音频文件
    with open(audioFile, mode = 'rb') as f:
        audioContent = f.read()

    host = 'nls-gateway-cn-shanghai.aliyuncs.com'

    # 设置HTTPS请求头部
    httpHeaders = {
        'X-NLS-Token': token,
        'Content-type': 'application/octet-stream',
        'Content-Length': len(audioContent)
        }


    # Python 2.x使用httplib
    # conn = httplib.HTTPConnection(host)

    # Python 3.x使用http.client
    conn = http.client.HTTPConnection(host)

    conn.request(method='POST', url=request, body=audioContent, headers=httpHeaders)

    response = conn.getresponse()
    print('Response status and response reason:')
    print(response.status ,response.reason)

    body = response.read()
    try:
        print('Recognize response is:')
        body = json.loads(body)
        print(body)

        status = body['status']
        if status == 20000000 :
            result = body['result']
            print('Recognize result: ' + result)
            return result
        else :
            print('Recognizer failed!')

    except ValueError:
        print('The response is not json format string')

    conn.close()
    
    
@app.route('/yuyinshibie/', methods=['POST'])
def yuyinshibie():
    f=request.files.get("file")
    yuzhong=request.form.get("yuzhong")
    file_path="./av/"+f.filename
    f.save(file_path)
    input_path = file_path
    output_path ="./av/out.wav"
    file1 = input_path
    file2 = output_path
    cmd = "C:/ffmpeg/bin/ffmpeg -i " + file1 + " -ar 16000 -ac 1 " + file2  #ffmpeg -i 输入文件 -ar 采样率  输出文件
    subprocess.call(cmd, shell=True)
    URL="wss://nls-gateway.cn-shanghai.aliyuncs.com/ws/v1"
    TOKEN=get_sdk()   #参考https://help.aliyun.com/document_detail/450255.html获取token
    APPKEY_putonghua="f7D7zKY0Rv5qvXIS"      #获取Appkey请前往控制台：https://nls-portal.console.aliyun.com/applist
    APPKEY_minnanyu="hSieLZdWnhhCCMQ6"
    APPKEY_yueyu="D5F19lhrDqE5KeTp"
    APPKEY_zhejianghua="GZltOqTnJBLk7PKQ"
    APPKEY_sichuanhua="wYnGDkBdCBD1rIcG"
    APPKEY_shanghaihua="mrQCSkcwMQv0lQmq"
    if yuzhong=="中文":
        appKey = APPKEY_putonghua
    else:
        if yuzhong=="闽南话":
            appKey = APPKEY_minnanyu
        else:
            if yuzhong=="粤语":
                appKey = APPKEY_yueyu
            else:
                if yuzhong=="浙江话":
                    appKey = APPKEY_zhejianghua
                else:
                    if yuzhong=="四川话":
                        appKey =  APPKEY_sichuanhua
                    else:
                        appKey =  APPKEY_shanghaihua
    token = TOKEN
    print(appKey)
# 服务请求地址
    url = 'https://nls-gateway-cn-shanghai.aliyuncs.com/stream/v1/asr'
# 音频文件
    audioFile = output_path
    format = 'pcm'
    sampleRate = 16000
    enablePunctuationPrediction  = True
    enableInverseTextNormalization = True
    enableVoiceDetection  = False

    # 设置RESTful请求参数
    request1 = url + '?appkey=' + appKey
    request1 = request1 + '&format=' + format
    request1 = request1 + '&sample_rate=' + str(sampleRate)

    if enablePunctuationPrediction :
        request1 = request1 + '&enable_punctuation_prediction=' + 'true'

    if enableInverseTextNormalization :
        request1 = request1 + '&enable_inverse_text_normalization=' + 'true'

    if enableVoiceDetection :
        request1 = request1 + '&enable_voice_detection=' + 'true'

    print('Request: ' + request1)
    ans=process(request1, token, audioFile)
    os.remove(output_path)
    return jsonify({'status': 200, 'message': '成功', 'data': ans})
