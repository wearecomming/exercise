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
from sqlalchemy import extract

achievement_api = Blueprint('achievement_app', __name__,)

@app.route('/check_achievement/',methods=['GET'])
def check_achievement():
    user_id=request.args.get("id")
    obtain=request.args.get("obtain")
    use=User.query.get(user_id)
    ach=use.achievements
    ans=[]
    for a in ach:
        if a.obtain!=obtain:
            continue
        imgs=a.images
        file_path=None
        for imgx in imgs:
            file_path=imgx.path
            break
        x={
            "id":a.id,
            "picture":file_path,
            "achievement":a.achievement,
            "description":a.description
        }
    ans.append(x)
    data={
        "type":obtain,
        "list":ans
    }
    return jsonify({'status': 200, 'message': '成功查看', 'data': data})