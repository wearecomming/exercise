from flask import Flask,request,jsonify
import configs
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import LONGTEXT
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Date
from flask_cors import CORS, cross_origin


app = Flask(__name__)

cors = CORS(app)
# 加载配置文件
app.config.from_object(configs)
# db绑定app
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)  # 设置主键, 默认自增
    name = db.Column('username', db.String(20), unique=True)
    password=db.Column(db.String(16))
    tel=db.Column(db.String(16))
    number=db.Column(db.Integer)
    suggestion=db.Column(LONGTEXT)
    
class Record(db.Model):
    __tablename__ = 'Record'
    id = db.Column(db.Integer, primary_key=True)
    type1=db.Column(db.String(16))
    type2=db.Column(db.String(16))
    bill=db.Column(db.String(16))
    date=db.Column(db.String(20))
    money=db.Column(db.Float)
    froms=db.Column(db.String(20))
    value=db.Column(LONGTEXT)
    remarks=db.Column(LONGTEXT)
    tim=db.Column(db.String(20))
    datt=db.Column(DateTime)
    user_id = db.Column(db.Integer(),db.ForeignKey('User.id'))
    user = db.relationship('User', backref=db.backref('records'))
    
class ImageFile(db.Model):
    __tablename__ = 'ImageFile'
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(30), index=True)
    image = db.Column(db.LargeBinary(length=2048))
    path = db.Column(db.String(50), index=True)
    record_id = db.Column(db.Integer(),db.ForeignKey('Record.id'))
    record = db.relationship('Record', backref=db.backref('images'))
    achievement_id = db.Column(db.Integer(),db.ForeignKey('Achievement.id'))
    achievement = db.relationship('Achievement', backref=db.backref('images'))
    
class Achievement(db.Model):
    __tablename__ = 'Achievement'
    id = db.Column(db.Integer, primary_key=True)
    obtain=db.Column(db.String(10))
    achievement=db.Column(db.String(20))
    description=db.Column(db.String(100))
    user_id = db.Column(db.Integer(),db.ForeignKey('User.id'))
    user = db.relationship('User', backref=db.backref('achievements'))
    
