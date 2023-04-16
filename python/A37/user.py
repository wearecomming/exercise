from flask import Flask,request,jsonify
import configs
import redis
import os
import random
from sqlalchemy import or_
from flask import send_from_directory
from flask_sqlalchemy import SQLAlchemy
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkcore.auth.credentials import StsTokenCredential
from aliyunsdkdysmsapi.request.v20170525.SendSmsRequest import SendSmsRequest
#from flask_admin import Admin, BaseView, expose
from model import User,app,db
from  sqlalchemy.sql.expression import func

from flask import Blueprint
#from revChatGPT.V1 import Chatbot

#chatbot = Chatbot(config={
# "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1UaEVOVUpHTkVNMVFURTRNMEZCTWpkQ05UZzVNRFUxUlRVd1FVSkRNRU13UmtGRVFrRXpSZyJ9.eyJodHRwczovL2FwaS5vcGVuYWkuY29tL3Byb2ZpbGUiOnsiZW1haWwiOiIxODMwNjUzMDIzQHFxLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJnZW9pcF9jb3VudHJ5IjoiVVMifSwiaHR0cHM6Ly9hcGkub3BlbmFpLmNvbS9hdXRoIjp7InVzZXJfaWQiOiJ1c2VyLUVKbWZ0TDQ4TDdYamtMQnlRbnlaN1BRaiJ9LCJpc3MiOiJodHRwczovL2F1dGgwLm9wZW5haS5jb20vIiwic3ViIjoid2luZG93c2xpdmV8NzRlM2ZiMGU0ZTA5NDYzNCIsImF1ZCI6WyJodHRwczovL2FwaS5vcGVuYWkuY29tL3YxIiwiaHR0cHM6Ly9vcGVuYWkub3BlbmFpLmF1dGgwYXBwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE2Nzc4ODc5NzEsImV4cCI6MTY3OTA5NzU3MSwiYXpwIjoiVGRKSWNiZTE2V29USHROOTVueXl3aDVFNHlPbzZJdEciLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIG1vZGVsLnJlYWQgbW9kZWwucmVxdWVzdCBvcmdhbml6YXRpb24ucmVhZCBvZmZsaW5lX2FjY2VzcyJ9.0hp0evM8OytiLh0WRsF-ckLZXNhfoNtgzcwrkS7L3NIyO3geDREn1Ars7zhw49oGy48P_pIpMA6q9dS0bt3vgu3IvN8LiKnf35O4k4ZAPXde_3LG6uo_tKHysX4dNRuF_FzpK_g0lYmDev7ZuTDni7gSj3MfOOd57n50hFbAEwBusTiGZ5J7KwwqPBW4cbT08LNzKUKsNLgDnY5OIHCLn_59i_Ycc-G7gLf0qmvvFLuAXTydbksAD-kbdaQ9o6y2VRbRejoaWYP6sDuG9KAYHCnn2xoPNL4r_NC3whMr7SFaQKXCfcS7WV6sOrlTSTauuzYEcyPr9BndEgPHHmcBNA"
#
#})
 
user_api = Blueprint('user_app', __name__)

credentials = AccessKeyCredential('LTAI5tMpq1bfR6YwU97G1XY5', 'UY6Dfu2KxN1gmp7nz3V5jLwvLA6lZQ')
client = AcsClient(region_id='cn-hangzhou', credential=credentials)



pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
rd=redis.Redis(connection_pool=pool)



# 在这里初始化Flask Flask-SQLAlchemy Flask-Admin

def phonecheck(s):
    phoneprefix=['130','131','132','133','134','135','136','137','138','139','150','151','152','153','156','158','159','170','180','183','182','185','186','188','189']
    if len(s)>11 or len(s)<11: 
        return False
    else:
        if  s.isdigit():
            if s[:3] in phoneprefix:
                return True
            else:
                return False
        else:
            return False

   
@app.route('/register/',methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    tel=request.form.get('telephone')
    user_code=request.form.get('user_code')
    if not all([username,password,password2,tel,user_code]):
        return jsonify({'status': 400, 'message': '参数不完整', 'data': ''})
    elif password != password2:
        return jsonify({'status': 400, 'message': '两次密码不一致，请重新输入', 'data': ''})
    elif phonecheck(tel) is False:
        return jsonify({'status': 400, 'message': '手机号错误', 'data': ''})
    elif User.query.filter_by(name=username).all():
        return jsonify({'status': 400, 'message': '用户名已存在', 'data': ''})
    elif User.query.filter_by(tel=tel).all():
        return jsonify({'status': 400, 'message': '手机号已存在', 'data': ''})
    elif user_code!=rd.get(tel):
        return jsonify({'status': 400, 'message': '验证码错误', 'data': ''})
    else:
        new_user = User(name=username,password=password,tel=tel)
        db.session.add(new_user)
        db.session.commit()
        use={
            'id':new_user.id,
            'username' : username,
            'password' : password,
            'telephone':tel
        }
        return jsonify({'status': 201, 'message': '成功创建', 'data': use})
        
@app.route('/login/',methods=['POST'])
def login():
    username = request.form.get('telephone')
    password = request.form.get('password')
    if not all([username,password]):
        return jsonify({'status': 400, 'message': '参数不完整', 'data': ''})
    user = User.query.filter(User.tel==username,User.password==password).first()
    if user is None:
        return jsonify({'status': 404, 'message': '无此用户', 'data': ''})
    if user:
        use={
        'id': user.id,
        'username' : username,
        'password' : password,
        'telephone':user.tel
        }
        return jsonify({'status': 200, 'message': '登录成功', 'data': use})
    else:
        return jsonify({'status': 400, 'message': '用户名或者密码错误', 'data': ''})

@app.route('/login_telephone/',methods=['GET'])
def login_telephone():
    tel = request.form.get('telephone')
    user_code=request.form.get('user_code')
    send_code=rd.get(tel)
    if tel is None:
        return jsonify({'status': 400, 'message': '手机号为空', 'data': ''})
    if phonecheck(tel) is False:
        return jsonify({'status': 400, 'message': '手机号错误', 'data': ''})
    if user_code!=send_code:
        return jsonify({'status': 400, 'message': '验证码错误', 'data': ''})
    if User.query.filter_by(tel=tel).all() is None:
        return jsonify({'status': 400, 'message': '手机号未注册', 'data': ''})
    user = User.query.filter(User.tel==tel).first()
    use={
        'id':user.id,
        'username':user.name,
        'password':user.password,
        'telephone':user.tel,
    }
    return jsonify({'status': 200, 'message': '成功登录', 'data': use})

def get_code():
    code = ''
    for i in range(6):
        add = random.randint(0, 9)
        code += str(add)
    return code

@app.route('/send_text/',methods=['POST'])
def send_text():
    tel=request.form.get('telephone')
    if tel is None:
        return jsonify({'status': 400, 'message': '手机号为空', 'data': ''})
    if phonecheck(tel) is False:
        return jsonify({'status': 400, 'message': '手机号错误', 'data': ''})
    code=get_code()
    request1 = SendSmsRequest()
    request1.set_accept_format('json')
    request1.set_SignName("阿里云短信测试")
    request1.set_TemplateCode("SMS_154950909")
    request1.set_PhoneNumbers(tel)
    request1.set_TemplateParam("{\"code\":\""+code+"\"}")

    response = client.do_action_with_exception(request1)
    if 'OK' in str(response):
        rd.set(tel,code,ex=300)
        use={
            'telephone':tel,
            'code':code
        }
        return jsonify({'status': 200, 'message': '成功发送', 'data': use})
    else:
        return jsonify({'status': 400, 'message': '发送失败', 'data': ''})
    
@app.route('/delet_user/',methods=['POST'])
def delet_user():
    idd=request.form.get('id')
    u=User.query.get(idd)
    db.session.delete(u)
    db.session.commit()
