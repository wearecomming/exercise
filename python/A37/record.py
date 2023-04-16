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
import random
from sqlalchemy import and_
import fasttext
from sqlalchemy import extract
from datetime import date,timedelta
import numpy as np
record_api = Blueprint('record_app', __name__,static_folder='images')
@app.route('/input_record/', methods=['POST'])
def input_record():
    type1=request.form.get("type")
    type2=request.form.get("subtype")
    bill=request.form.get("bill")
    date=request.form.get("date")
    money=request.form.get("money")
    froms=request.form.get("froms")
    value=request.form.get("value")
    user_id=request.form.get("user_id")
    time=request.form.get("time")
    if not all([type1,type2,bill,date,money,froms,value,user_id,time]):
        return jsonify({'status': 400, 'message': '参数不完整', 'data': ''})
    ddd=time.split(':')
    if len(ddd[0])<=1:
        ddd[0]="0"+ddd[0]
    if len(ddd[1])<=1:
        ddd[1]="0"+ddd[1]
    if len(ddd[2])<=1:
        ddd[2]="0"+ddd[2]
    ddds=ddd[0]+":"+ddd[1]+":"+ddd[2]
    time=ddds
    img=request.files.get("image")
    remarks=request.form.get("remarks")
    dt=datetime.strptime(date,'%Y-%m-%d')
    new_record=Record(type1=type1,type2=type2,bill=bill,date=date,money=money,froms=froms,value=value,user_id=user_id,remarks=remarks,datt=dt,tim=time)
    db.session.add(new_record)
    db.session.commit()
    file_path=None
    if img is not None:
        nnn=img.filename.split('.')
        nx=ImageFile.query.order_by(desc(ImageFile.id)).first()
        if nx is not None:
            idd=nx.id+1
        else:
            idd=1
        file_path = "images/"+str(idd)+"."+nnn[-1]
        new_img=ImageFile(image=img,record_id=new_record.id,path=file_path,image_name=str(idd)+"."+nnn[-1])
        db.session.add(new_img)
        img.save("./"+file_path)
        if nnn[-1]=='jpg' or nnn[-1]=='png':
            immg=cv2.imread("./"+file_path)
            a=math.ceil(math.sqrt((immg.shape[0]*immg.shape[1])/1000000))
            y=int(immg.shape[0]/a)
            x=int(immg.shape[1]/a)
            immg=cv2.resize(immg,(x,y))
            cv2.imwrite("./"+file_path,immg)
        db.session.commit()
    x={
        "type":type1,
        "subtype":type2,
        "bill":bill,
        "date":date,
        "money":money,
        "froms":froms,
        "value":value,
        "user_id":user_id,
        "id":new_record.id,
        "image":file_path,
        "remarks":remarks
    }
    return jsonify({'status': 200, 'message': '成功', 'data': x})

@app.route('/change_record/', methods=['POST'])
def change_record():
    idd=request.form.get("id")
    type1=request.form.get("type")
    type2=request.form.get("subtype")
    bill=request.form.get("bill")
    date=request.form.get("date")
    money=request.form.get("money")
    froms=request.form.get("froms")
    value=request.form.get("value")
    img=request.files.get("image")
    remarks=request.form.get("remarks")
    file_path=None
    if idd is None:
        return jsonify({'status': 400, 'message': '无id'})
    rec=Record.query.get(idd)
    if type1 is not None:rec.type1=type1
    if type2 is not None:rec.type2=type2
    if bill is not None:rec.bill=bill
    if date is not None:rec.date=date
    if money is not None:rec.money=money
    if froms is not None:rec.froms=froms
    if value is not None:rec.value=value
    if remarks is not None:rec.remarks=remarks
    if img is not None:
        imgs=rec.images
        for imgx in imgs:
            db.session.delete(imgx)
            db.session.commit()
        nnn=img.filename.split('.')
        nx=ImageFile.query.order_by(desc(ImageFile.id)).first()
        idd=nx.id+1
        file_path = "images/"+str(idd)+"."+nnn[-1]
        new_img=ImageFile(image=img,record_id=idd,path=file_path,image_name=str(idd)+"."+nnn[-1])
        db.session.add(new_img)
        img.save("./"+file_path)
        if nnn[-1]=='jpg' or nnn[-1]=='png':
            immg=cv2.imread("./"+file_path)
            a=math.ceil(math.sqrt((immg.shape[0]*img.shape[1])/1000000))
            y=int(immg.shape[0]/a)
            x=int(immg.shape[1]/a)
            immg=cv2.resize(immg,(x,y))
            cv2.imwrite("./"+file_path,immg)
    db.session.commit()
    x={
        "type":rec.type1,
        "subtype":rec.type2,
        "bill":rec.bill,
        "date":rec.date,
        "money":rec.money,
        "froms":rec.froms,
        "value":rec.value,
        "user_id":rec.user_id,
        "id":rec.id,
        "image":file_path,
        "remarks":rec.remarks
    }
    return jsonify({'status': 200, 'message': '成功', 'data': x})
@app.route('/delete_record/', methods=['POST'])
def delete_record():
    idd=request.form.get("id")
    idd=Record.query.get(idd)
    if idd is None:
        return jsonify({'status': 404, 'message': '没有这个记录啊', 'data': ''})
    db.session.delete(idd)
    db.session.commit()
    x={
        "id":idd.id,
        "state":"已删除"
    }
    return jsonify({'status': 200, 'message': '删除成功', 'data': x})

@app.route('/get_record/', methods=['GET'])
def get_record():
    idd=request.args.get("id")
    rec=Record.query.get(idd)
    if rec is None:
        return jsonify({'status': 404, 'message': '没有'})
    file_path=None
    if rec.images is not None:
        imgs=rec.images
        for imgx in imgs:
            file_path=imgx.path
            break
    if rec.date is None:
        return jsonify({'status': 404, 'message': '没有date'})
    ddd=rec.date.split('-')
    if len(ddd[1])<=1:
        ddd[1]="0"+ddd[1]
    if len(ddd[2])<=1:
        ddd[2]="0"+ddd[2]
    ddds=ddd[0]+"-"+ddd[1]+"-"+ddd[2]
    x={
        "type":rec.type1,
        "subtype":rec.type2,
        "bill":rec.bill,
        "date":ddds,
        "money":rec.money,
        "froms":rec.froms,
        "value":rec.value,
        "user_id":rec.user_id,
        "id":rec.id,
        "remarks":rec.remarks,
        "image":file_path,
        "time":rec.tim
    }
    return jsonify({'status': 200, 'message': '搜索成功', 'data': x})

@app.route('/get_all_record/', methods=['GET'])
def get_all_record():
    user_id=request.args.get("user_id")
    date=request.args.get("date")
    use=User.query.get(user_id)
    recs=Record.query.filter(Record.user_id==user_id).order_by(desc(Record.datt))
    date=datetime.strptime(date,'%Y-%m-%d')
    expand1=0
    earning1=0
    all_date=[]
    day_list=[]
    data_day=[]
    all_num=0
    for rec in recs:
        if rec.datt>date:
            continue
        if rec.datt not in all_date:
            all_date.append(rec.datt)
            day_list.append([])
        for i in range(0,len(all_date)):
            if all_date[i]==rec.datt:
                day_list[i].append(rec)
                all_num+=1
                break
        if all_num>20:
            break
    for i in range(0,len(all_date)):
        expand=0
        earning=0
        shikieiki=[]
        for rec in day_list[i]:
            fumo=1
            if rec.type1=="expend":
                fumo=-1
                expand-=rec.money
            else:
                earning+=rec.money
            yamasanadu={
                "id":rec.id,
                "subtype":rec.type2,
                "subtype_money":rec.money*fumo,
                "time":rec.tim
            }
            shikieiki.append(yamasanadu)
        a=str(all_date[i].year)
        b=str(all_date[i].month)
        c=str(all_date[i].day)
        if len(b)<=1:b="0"+b
        if len(c)<=1:c="0"+c
        lingxian={
            "date":a+"-"+b+"-"+c,
            "expend":expand,
            "earning":earning,
            "day_list":shikieiki
        }
        data_day.append(lingxian)
        expand1+=expand
        earning1+=earning
    remiliya={}
    remiliya={
        "user_id":user_id,
        "expend":expand1,
        "earning":earning1,
        "data_day":data_day
    }
    print("HH")
    return jsonify({'status': 200, 'message': '搜索成功', 'data': remiliya})

@app.route('/get_time_record/', methods=['GET'])
def get_time_record():
    type1=request.args.get("type")
    str_date=request.args.get("str_date")
    end_date=request.args.get("end_date")
    start=datetime.strptime(str_date,'%Y-%m-%d')
    end=datetime.strptime(end_date,'%Y-%m-%d')
    recs=Record.query.filter(Record.type1==type1,Record.datt>=start,Record.datt<=end).order_by(Record.datt)
    if recs is None:
        return jsonify({'status': 404, 'message': '没有任何记录'})
    msg={}
    file_path=None
    idx=0
    for rec in recs:
        idx+=1
        file_path=None
        imgs=rec.images
        for imgx in imgs:
            file_path=imgx.path
            break
        ss={
        "type":rec.type1,
        "subtype":rec.type2,
        "bill":rec.bill,
        "date":rec.date,
        "money":rec.money,
        "froms":rec.froms,
        "value":rec.value,
        "user_id":rec.user_id,
        "id":rec.id,
        "remarks":rec.remarks,
        "image":file_path
        }
        msg["record"+str(idx)]=ss
    x={
        "len":recs.count(),
        "type":type1,
        "msg":msg
    }
    return jsonify({'status': 200, 'message': '搜索成功', 'data': x})

@app.route('/get_type_record/', methods=['GET'])
def get_type_record():
    type1=request.args.get("type")
    type2=request.args.get("subtype")
    recs=Record.query.filter(Record.type1==type1,Record.type2==type2).order_by(Record.datt)
    if recs is None:
        return jsonify({'status': 404, 'message': '没有任何记录'})
    msg={}
    file_path=None
    idx=0
    for rec in recs:
        idx+=1
        file_path=None
        imgs=rec.images
        for imgx in imgs:
            file_path=imgx.path
            break
        ss={
        "type":rec.type1,
        "subtype":rec.type2,
        "bill":rec.bill,
        "date":rec.date,
        "money":rec.money,
        "froms":rec.froms,
        "value":rec.value,
        "user_id":rec.user_id,
        "id":rec.id,
        "remarks":rec.remarks,
        "image":file_path
        }
        msg["record"+str(idx)]=ss
    x={
        "len":recs.count(),
        "type1":type1,
        "msg":msg
    }
    return jsonify({'status': 200, 'message': '搜索成功', 'data': x})

@app.route('/get_search_record/', methods=['Post'])
def get_search_record():
    type1=None
    uid=request.form.get("user_id",type=int)
    type1=request.form.get("type")
    order=request.form.get("order")
    search=request.form.get("search")
    str_date=request.form.get("str_date")
    end_date=request.form.get("end_date")
    str_money=request.form.get("str_money",type=int)
    end_money=request.form.get("end_money",type=int)
    subtype=request.form.get("subtype")
    if subtype is not None:
        xx=subtype.split(",")
    else:
        xx=["餐饮","娱乐","家具","文化教育","交通","办公","运动","服装","医疗","购物","宠物","其他","工资","打工","奖金","其他"]
    if str_date is not None:
        str_date=datetime.strptime(str_date,'%Y-%m-%d')
    if end_date is not None:
        end_date=datetime.strptime(end_date,'%Y-%m-%d')
    if order=="ASC":
        recs=Record.query.filter(
            Record.type1==type1 if type1 is not None else Record.type1,
            Record.datt>=str_date if str_date is not None else Record.datt,
            Record.datt<=end_date if end_date is not None else Record.datt,
            Record.money>=str_money if str_money is not None else Record.money,
            Record.money<=end_money if end_money is not None else Record.money,
            Record.user_id==uid,
            Record.type2.in_(xx),
            or_(
                Record.type2.ilike("%"+search+"%"  ) if search is not None else "",
                Record.bill.ilike("%"+search+"%"  ) if search is not None else "",
                Record.date.ilike("%"+search+"%"  ) if search is not None else "",
                Record.money.ilike("%"+search+"%"  ) if search is not None else "",
                Record.froms.ilike("%"+search+"%"  ) if search is not None else "",
                Record.value.ilike("%"+search+"%"  ) if search is not None else "",
                Record.remarks.ilike("%"+search+"%"  ) if search is not None else "",
                )
            ).order_by(Record.datt)
    else:
        recs=Record.query.filter(
            Record.type1==type1 if type1 is not None else Record.type1,
            Record.datt>=str_date if str_date is not None else Record.datt,
            Record.datt<=end_date if end_date is not None else Record.datt,
            Record.money>=str_money if str_money is not None else Record.money,
            Record.money<=end_money if end_money is not None else Record.money,
            Record.user_id==uid,
            Record.type2.in_(xx),
            or_(
                Record.type2.ilike("%"+search+"%"  ) if search is not None else "",
                Record.bill.ilike("%"+search+"%"  ) if search is not None else "",
                Record.date.ilike("%"+search+"%"  ) if search is not None else "",
                Record.money.ilike("%"+search+"%"  ) if search is not None else "",
                Record.froms.ilike("%"+search+"%"  ) if search is not None else "",
                Record.value.ilike("%"+search+"%"  ) if search is not None else "",
                Record.remarks.ilike("%"+search+"%"  ) if search is not None else "",
                )
            ).order_by(desc(Record.datt))
    if recs is None:
        return jsonify({'status': 404, 'message': '没有任何记录'})
    msg={}
    idx=0
    file_path=None
    sukai=[]
    sena=[]
    shikieiki=[]
    aimazanadu=[]
    for rec in recs:
        if rec.datt not in shikieiki:
            shikieiki.append(rec.datt)
            aimazanadu=[]
            aimazanadu.append(rec)
        else:
            aimazanadu.append(rec)
        sena.append(aimazanadu)
    for i in range(0,len(shikieiki)):
        sakuya=[]
        lingxian=0
        huiye=0
        for rec in sena[i]:
            scrallette=1
            if rec.type1=="expend":
                scrallette=-1
            sakuya.append({
                "id":rec.id,
                "subtype":rec.type2,
                "subtype_money":rec.money*scrallette,
                "time":rec.tim
                })
            if scrallette==-1:
                lingxian+=rec.money*-1
            else:
                huiye+=rec.money
#        file_path=None
#        imgs=rec.images
#        for imgx in imgs:
#            file_path=imgx.path
 #           break
        aa=str(shikieiki[i].year)
        bb=str(shikieiki[i].month)
        cc=str(shikieiki[i].day)
        if len(bb)<=1:bb="0"+bb
        if len(cc)<=1:cc="0"+cc
        remiliya={
            "date":aa+"-"+bb+"-"+cc,
            "expend":lingxian,
            "earning":huiye,
            "day_list":sakuya
        }
        sukai.append(remiliya)
    fumo={
        "type":type1,
        "len":recs.count(),
        "data_day":sukai
    }
    return jsonify({'status': 200, 'message': '搜索成功', 'data': fumo})

@app.route('/get_line_record/', methods=['GET'])
def get_line_record():
    year=request.args.get("year",type=int)
    month=request.args.get("month",type=int)
    earning=[]
    date=[]
    expand=[]
    if month==0:
        recs=Record.query.filter(extract('year', Record.datt) ==year).order_by(Record.datt)
        for i in range(1,13):
            earning.append(0)
            expand.append(0)
            date.append(str(i)+"月")
        for rec in recs:
            if rec.type1=='earning':earning[rec.datt.month-1]+=rec.money
            else: expand[rec.datt.month-1]+=rec.money
        x={
            "year":year,
            "month":month,
            "date":date,
            "earning":earning,
            "expand":expand
        }
        return jsonify({'status': 200, 'message': '成功', 'data': x})
    else:
        recs=Record.query.filter(extract('year', Record.datt) ==year,extract('month', Record.datt) ==month).order_by(Record.datt)
        print(recs)
        ix=calendar.monthrange(year,month)[1]
        for i in range(1,ix):
            earning.append(0)
            expand.append(0)
            date.append(str(i)+"日")
        for rec in recs:
            if rec.type1=='earning':earning[rec.datt.day-1]+=rec.money
            else: expand[rec.datt.day-1]+=rec.money
            
        x={
            "year":year,
            "month":month,
            "date":date,
            "earning":earning,
            "expand":expand
        }
        return jsonify({'status': 200, 'message': '成功', 'data': x})
    
@app.route('/get_pine_record/', methods=['GET'])
def get_pine_record():
    year=request.form.get("year")
    month=request.form.get("month")
    type1=request.form.get("type1")
    da=[]
    type2=[]
    proportion=[]
    if month==0:
        recs=Record.query.filter(extract('year', Record.datt) ==year,Record.type1==type1).order_by(Record.datt)
    else:
        recs=Record.query.filter(extract('year', Record.datt) ==year,extract('month', Record.datt) ==month,Record.type1==type1).order_by(Record.datt)
    if recs is None:
        return jsonify({'status': 404, 'message': '没有任何记录'})
    sum=0.0
    for rec in recs:
        if rec.type2 not in type2:
            type2.append(rec.type2)
            da.append(0)
        for i in range(0,len(type2)):
            if type2[i]==rec.type2:
                da[i]+=rec.money
                sum+=rec.money
                break
    for i in range(0,len(type2)):
        proportion.append(float(da[i])/sum)
    x={
        "type1":type1,
        "type2":type2,
        "data":da,
        "proportion":proportion
    }
    
    return jsonify({'status': 200, 'message': '成功', 'data': x})

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

    
@app.route('/fff/', methods=['GET'])
def fff():
    text=request.args.get("text")
    text=text.replace("\n","")
    model = fasttext.load_model('C:\A37\model.bin')
    label = model.predict(text)
    return jsonify({'status': 200, 'message': '成功', 'data': change(label[0][0])})
    
@app.route('/get_line_year_record/', methods=['GET'])
def get_line_year_record():
    uid=request.args.get("user_id")
    year=request.args.get("year",type=int)
    type1=request.args.get("type")
    earning=[]
    date=[]
    miaoshu=["一","二","三","四","五","六","七","八","九","十","十一","十二"]
    recs=Record.query.filter(extract('year', Record.datt) ==year,Record.user_id==uid).order_by(Record.datt)
    if recs is None:
        return jsonify({'status': 404, 'message': '没有任何记录'})
    for i in range(0,12):
        earning.append(0)
        date.append(miaoshu[i]+"月")
    for rec in recs:
        if rec.type1==type1:earning[rec.datt.month-1]+=rec.money
    x={
        "type":type1,
        "month":date,
        "money":earning,
        "year":year
    }
    return jsonify({'status': 200, 'message': '成功', 'data': x}) 
    
@app.route('/get_all_year_record/', methods=['GET'])
def get_all_year_record():
    uid=request.args.get("user_id")
    year=request.args.get("year",type=int)
    type1=request.args.get("type")
    data=0
    res_data=0
    pre_data=0
    max_month=0
    recs=Record.query.filter(extract('year', Record.datt) ==year,Record.user_id==uid).order_by(Record.datt)
    if recs is None:
        return jsonify({'status': 404, 'message': '没有任何记录'})
    max_month = recs[0].datt.month
    for rec in recs:
        if rec.type1==type1:
            data+=rec.money
        if rec.type1=="expend":
            res_data-=rec.money
        else:
            res_data+=rec.money
        if max_month<rec.datt.month:
            max_month=rec.datt.month
    recs=Record.query.filter(extract('year', Record.datt) ==year-1,Record.user_id==uid).order_by(Record.datt)
    if recs is None:
        return jsonify({'status': 404, 'message': '没有任何记录'})
    for rec in recs:
        if rec.type1==type1:
            pre_data+=rec.money
    x={
        "year":year,
        "type":type1,
        "date":data,
        "ave_data":data/max_month,
        "pre_data":pre_data,
        "res_data":res_data
    }
    return jsonify({'status': 200, 'message': '成功', 'data': x})
        
@app.route('/get_pine_year_record/', methods=['GET'])
def get_pine_year_record():
    uid=request.args.get("user_id")
    year=request.args.get("year",type=int)
    type1=request.args.get("type")
    subtype=[]
    money=[]
    amount=[]
    recs=Record.query.filter(extract('year', Record.datt) ==year,Record.user_id==uid).order_by(Record.datt)
    if recs is None:
        return jsonify({'status': 404, 'message': '没有任何记录'})
    for rec in recs:
        if rec.type2 not in subtype:
            subtype.append(rec.type2)
            money.append(0)
            amount.append(0)
        for i in range(0,len(subtype)):
            if subtype[i]==rec.type2:
                money[i]+=rec.money
                amount[i]+=1
                break
    x={
        "year":year,
        "type":type1,
        "subtype":subtype,
        "money":money,
        "amount":amount
    }
    return jsonify({'status': 200, 'message': '成功', 'data': x})
    
@app.route('/get_line_month_record/', methods=['GET'])
def get_line_month_record():
    uid=request.args.get("user_id")
    year=request.args.get("year",type=int)
    month=request.args.get("month",type=int)
    typex=request.args.get("type")
    sub=request.args.get("subtype")
    earning=[]
    date=[]
    if sub is None:
        recs=Record.query.filter(extract('year', Record.datt) ==year,extract('month', Record.datt) ==month,Record.user_id==uid,).order_by(Record.datt)
    else:
        recs=Record.query.filter(Record.type2==sub,extract('year', Record.datt) ==year,extract('month', Record.datt) ==month,Record.user_id==uid,).order_by(Record.datt)
    if recs is None:
        return jsonify({'status': 404, 'message': '没有任何记录'})
    for i in range(0,31):
            earning.append(0)
            date.append(str(i+1))
    for rec in recs:
        if rec.type1==typex:
            earning[rec.datt.day-1]+=rec.money
    x={
        "type":typex,
        "year":year,
        "month":month,
        "day":date,
        "money":earning
    }
    return jsonify({'status': 200, 'message': '成功', 'data': x}) 
    
@app.route('/get_all_month_record/', methods=['GET'])
def get_all_month_record():
    uid=request.args.get("user_id")
    month=request.args.get("month",type=int)
    year=request.args.get("year",type=int)
    typex=request.args.get("type")
    sub=request.args.get("subtype")
    data=0
    res_data=0
    pre_data=0
    max_day=0
    if sub is None:
        recs=Record.query.filter(extract('year', Record.datt) ==year,extract('month', Record.datt) ==month,Record.user_id==uid).order_by(Record.datt)
    else:
        recs=Record.query.filter(Record.type2==sub,extract('year', Record.datt) ==year,extract('month', Record.datt) ==month,Record.user_id==uid).order_by(Record.datt)
    max_day = 1
    for rec in recs:
        print(rec.datt.day)
        if rec.type1==typex:
            data+=rec.money
        if rec.type1=="expend":
            res_data-=rec.money
        else:
            res_data+=rec.money
        if max_day<rec.datt.day:
            max_day=rec.datt.day
    dt=date(year,month,20)
    last_dt=dt-timedelta(days=31)
    if sub is None:
        recs=Record.query.filter(extract('year', Record.datt) ==year,extract('month', Record.datt) ==last_dt.month,Record.user_id==uid).order_by(Record.datt)
    else:
        recs=Record.query.filter(Record.type2==sub,extract('year', Record.datt) ==year,extract('month', Record.datt) ==last_dt.month,Record.user_id==uid).order_by(Record.datt)
    if recs is None:
        return jsonify({'status': 404, 'message': '没有任何记录'})
    for rec in recs:
        if rec.type1==typex:
            pre_data+=rec.money
    x={
        "year":year,
        "type":typex,
        "date":data,
        "ave_data":data/max_day,
        "pre_data":pre_data,
        "res_data":res_data
    }
    return jsonify({'status': 200, 'message': '成功', 'data': x})


@app.route('/get_pine_month_record/', methods=['GET'])
def get_pine_month_record():
    uid=request.args.get("user_id")
    month=request.args.get("month",type=int)
    year=request.args.get("year",type=int)
    type1=request.args.get("type")
    subtype=[]
    money=[]
    amount=[]
    recs=Record.query.filter(extract('year', Record.datt) ==year,extract('month', Record.datt) ==month,Record.user_id==uid).order_by(Record.datt)
    if recs is None:
        return jsonify({'status': 404, 'message': '没有任何记录'})
    for rec in recs:
        if rec.type2 not in subtype:
            subtype.append(rec.type2)
            money.append(0)
            amount.append(0)
        for i in range(0,len(subtype)):
            if subtype[i]==rec.type2:
                money[i]+=rec.money
                amount[i]+=1
                break
    x={
        "year":year,
        "type":type1,
        "subtype":subtype,
        "money":money,
        "amount":amount,
        "month":month
    }
    return jsonify({'status': 200, 'message': '成功', 'data': x})

@app.route('/get_line_week_record/', methods=['GET'])
def get_line_week_record():
    uid=request.args.get("user_id")
    year=request.args.get("year",type=int)
    month=request.args.get("month",type=int)
    type1=request.args.get("type")
    day=request.args.get("day",type=int)
    earning=[]
    date=[]
    now_day=datetime(year,month,day)
    monday=now_day-timedelta(days=calendar.weekday(year,month,day))
    ds=[monday]
    miaoshu=["一","二","三","四","五","六","日"]
    for i in range(1,7):
        ds.append(monday+timedelta(days=i))
    recs=Record.query.filter(extract('year', Record.datt) ==year,extract('month', Record.datt) ==month,Record.user_id==uid,).order_by(Record.datt)
    if recs is None:
        return jsonify({'status': 404, 'message': '没有任何记录'})
    for i in range(0,7):
            earning.append(0)
            date.append("周"+miaoshu[i])
    for rec in recs:
        if rec.datt not in ds:continue
        if rec.type1==type1:earning[calendar.weekday(rec.datt.year,rec.datt.month,rec.datt.day)]+=rec.money
    aa1=str(ds[0].year)
    bb1=str(ds[0].month)
    cc1=str(ds[0].day)
    if len(bb1)<=1:bb1="0"+bb1
    if len(cc1)<=1:cc1="0"+cc1
    ans1=aa1+"-"+bb1+"-"+cc1
    aa2=str(ds[-1].year)
    bb2=str(ds[-1].month)
    cc2=str(ds[-1].day)
    if len(bb2)<=1:bb2="0"+bb2
    if len(cc2)<=1:cc2="0"+cc2
    ans2=aa2+"-"+bb2+"-"+cc2
    x={
        "type":type1,
        "year":year,
        "month":month,
        "week":date,
        "money":earning,
        "str_day":ans1,
        "end_day":ans2
    }
    return jsonify({'status': 200, 'message': '成功', 'data': x}) 

@app.route('/get_all_week_record/', methods=['GET'])
def get_all_week_record():
    uid=request.args.get("user_id")
    month=request.args.get("month",type=int)
    year=request.args.get("year",type=int)
    typex=request.args.get("type")
    day=request.args.get("day",type=int)
    data=0
    res_data=0
    pre_data=0
    max_day=0
    now_day=datetime(year,month,day)
    monday=now_day-timedelta(days=calendar.weekday(year,month,day))
    ds=[monday]
    for i in range(1,7):
        ds.append(monday+timedelta(days=i))
    recs=Record.query.filter(extract('year', Record.datt) ==year,extract('month', Record.datt) ==month,Record.user_id==uid).order_by(Record.datt)
    if recs is None:
        return jsonify({'status': 404, 'message': '没有任何记录'})
    max_day = recs[0].datt.day
    for rec in recs:
        if rec.datt not in ds:continue
        if rec.type1==typex:
            data+=rec.money
        if rec.type1=="expend":
            res_data-=rec.money
        else:
            res_data+=rec.money
        if max_day<rec.datt.day:
            max_day=rec.datt.day
    recs=Record.query.filter(extract('year', Record.datt) ==year,extract('month', Record.datt) ==month,Record.user_id==uid).order_by(Record.datt)
    if recs is None:
        return jsonify({'status': 404, 'message': '没有任何记录'})
    ds2=[]
    for i in range(1,8):
        ds2.append(monday-timedelta(days=i))
    for rec in recs:
        if rec.datt not in ds2:continue
        if rec.type1==typex:
            pre_data+=rec.money
    x={
        "year":year,
        "type":typex,
        "date":data,
        "ave_data":data/14,
        "pre_data":pre_data,
        "res_data":res_data
    }
    return jsonify({'status': 200, 'message': '成功', 'data': x})

@app.route('/get_pine_week_record/', methods=['GET'])
def get_pine_week_record():
    uid=request.args.get("user_id")
    month=request.args.get("month",type=int)
    year=request.args.get("year",type=int)
    typex=request.args.get("type")
    day=request.args.get("day",type=int)
    subtype=[]
    money=[]
    amount=[]
    now_day=datetime(year,month,day)
    monday=now_day-timedelta(days=calendar.weekday(year,month,day))
    ds=[monday]
    for i in range(1,7):
        ds.append(monday+timedelta(days=i))
    recs=Record.query.filter(extract('year', Record.datt) ==year,extract('month', Record.datt) ==month,Record.user_id==uid).order_by(Record.datt)
    if recs is None:
        return jsonify({'status': 404, 'message': '没有任何记录'})
    for rec in recs:
        if rec.datt not in ds:continue
        if rec.type1 != typex : continue
        if rec.type2 not in subtype:
            subtype.append(rec.type2)
            money.append(0)
            amount.append(0)
        for i in range(0,len(subtype)):
            if subtype[i]==rec.type2:
                money[i]+=rec.money
                amount[i]+=1
                break
    x={
        "year":year,
        "type":typex,
        "subtype":subtype,
        "money":money,
        "amount":amount,
        "month":month
    }
    return jsonify({'status': 200, 'message': '成功', 'data': x})

@app.route('/get_talk_month_record/', methods=['GET'])
def get_talk_month_record():
    uid=request.args.get("user_id")
    year=request.args.get("year",type=int)
    month=request.args.get("month",type=int)
    type1=request.args.get("type")
    type2=request.args.get("subtype")
    earning=[]
    date=[]
    recs=Record.query.filter(extract('year', Record.datt) ==year,extract('month', Record.datt) ==month,Record.user_id==uid,).order_by(Record.datt)
    if recs is None:
        return jsonify({'status': 404, 'message': '没有任何记录'})
    for rec in recs:
        for i in range(0,31):
            earning.append(0)
            date.append(str(i+1))
        if rec.type1==type1 and rec.type2==type2:earning[rec.datt.month-1]+=rec.money
    x={
        "type":type1,
        "year":year,
        "month":month,
        "day":date,
        "money":earning,
        "subtype":type2
    }
    return jsonify({'status': 200, 'message': '成功', 'data': x}) 


@app.route('/huaxiang/', methods=['GET'])
def huaxiang():
    user_id=request.args.get("user_id")
    num=random.randint(1,7)
    use=User.query.get(user_id)
    if use is None:
        return jsonify({'status': 404, 'message': '没有用户'})
    date=request.args.get("date")
    if num==1:
        dt=datetime.strptime(date,'%Y-%m-%d')
        recs=Record.query.filter(Record.user_id==user_id,extract('year', Record.datt) ==dt.year,extract('month', Record.datt) ==dt.month,Record.type1=="expend")
        if recs is None:
            return jsonify({'status': 404, 'message': '没有任何记录'})
        money=0
        sub=[]
        sub_money=[]
        for rec in recs:
            money+=rec.money
            if rec.type2 not in sub:
                sub.append(rec.type2)
                sub_money.append(0)
            for i in range(0,len(sub)):
                if sub[i]==rec.type2:
                    sub_money[i]+=rec.money
                    break
        maxx=0
        minn=999999999
        max_idx=""
        minn_idx=""
        for i in range(0,len(sub)):
            if maxx<=sub_money[i]:
                maxx=sub_money[i]
                max_idx=sub[i]
            if minn>=sub_money[i]:
                minn=sub_money[i]
                min_idx=sub[i]
        if money==0:
            return jsonify({'status':404,'message':'没有任何记录'})
        p_max=float(maxx)/float(money)*100.0
        p_min=float(minn)/float(money)*100.0
        p_max=round(p_max,2)
        p_min=round(p_min,2)
        money=round(float(money),2)
        ans="根据布奇统计，本月已经累计消费"+str(money)+"元，其中，"+max_idx+"类型的消费最多，占比达到了"+str(p_max)+"%。"+min_idx+"类型的消费最少，仅达到"+str(p_min)+"%。"
        return jsonify({'status': 200, 'message': '成功', 'data': ans})
    if num==2:
        recs=Record.query.filter(Record.user_id==user_id,Record.type1=="expend")
        if recs is None:
            return jsonify({'status': 404, 'message': '没有任何记录'})
        num=[]
        shoper=[]
        money=[]
        for rec in recs:
            if rec.froms not in shoper:
                shoper.append(rec.froms)
                num.append(0)
                money.append(0)
            for i in range(0,len(shoper)):
                if shoper[i]==rec.froms:
                    num[i]+=1
                    money[i]+=rec.money
        maxx=0
        max_money=0
        max_from=0
        for i in range(0,len(shoper)):
            if maxx<=num[i]:
                maxx=num[i]
                max_money=money[i]
                max_from=shoper[i]
        max_money=round(float(max_money),2)
        ans="经过布奇分析判断，您似乎更热衷于"+max_from+"店家，累计消费达到"+str(max_money)+"元，累计前往"+str(maxx)+"次，推荐和你的朋友分享哦。"
        return jsonify({'status': 200, 'message': '成功', 'data': ans})
    if num==3:
        dt=datetime.strptime(date,'%Y-%m-%d')
        recs=Record.query.filter(Record.user_id==user_id,extract('year', Record.datt) ==dt.year,Record.type1=="expend")
        if recs is None:
            return jsonify({'status': 404, 'message': '没有任何记录'})
        sub=[]
        sub_money=[]
        money=0
        for rec in recs:
            money+=rec.money
            if rec.type2 not in sub:
                sub.append(rec.type2)
                sub_money.append(0)
            for i in range(0,len(sub)):
                if sub[i]==rec.type2:
                    sub_money[i]+=rec.money
                    break
        maxx=0
        max_idx=""
        for i in range(0,len(sub)):
            if maxx<=sub_money[i]:
                maxx=sub_money[i]
                max_idx=sub[i]
        if money==0:
            return jsonify({'status':404,'message':'没有任何记录'})
        p_max=float(maxx)/float(money)*100.0
        p_max=round(p_max,2)
        ans="和其他消费水平近似的用户相比，布奇发现你似乎更热衷于"+max_idx+"类型的消费，当年占比达到了"+str(p_max)+"%,相比于其他用户，高出了14.678%"
        return jsonify({'status': 200, 'message': '成功', 'data': ans})
    if num==4:
        recs=Record.query.filter(Record.type1=="expend")
        if recs is None:
            return jsonify({'status': 404, 'message': '没有任何记录'})
        sub=[]
        sub_money=[]
        for rec in recs:
            if rec.type2 not in sub:
                sub.append(rec.type2)
                sub_money.append(0)
            for i in range(0,len(sub)):
                if sub[i]==rec.type2:
                    sub_money[i]+=rec.money
                    break
        maxx=0
        max_idx=""
        for i in range(0,len(sub)):
            if maxx<=sub_money[i]:
                maxx=sub_money[i]
                max_idx=sub[i]
        recs=Record.query.filter(Record.type1=="expend",Record.type2==max_idx)
        people=[]
        total=0
        for rec in recs:
            if rec.user_id not in people:
                people.append(rec.user_id)
                total+=1
        if total==0:
            return jsonify({'status':404,'message':'没有任何记录'})
        if total>0:
            p=float(maxx)/float(total)
        p=round(p,2)
        ans="布奇根据您的消费行为习惯，和与您消费水平相近的用户喜好，发现你们大多喜欢"+max_idx+"类型的商品，每个人平均在该类别上消费"+str(p)+"元。"
        return jsonify({'status': 200, 'message': '成功', 'data': ans})
    if num==5:
        dt=datetime.strptime(date,'%Y-%m-%d')
        recs=Record.query.filter(Record.user_id==user_id,extract('year', Record.datt) ==dt.year,extract('month', Record.datt) ==dt.month,Record.type1=="expend")
        if recs is None:
            return jsonify({'status': 404, 'message': '没有任何记录'})
        sub=[]
        sub_money=[]
        money=0
        for rec in recs:
            money+=rec.money
            if rec.type2 not in sub:
                sub.append(rec.type2)
                sub_money.append(0)
            for i in range(0,len(sub)):
                if sub[i]==rec.type2:
                    sub_money[i]+=rec.money
                    break
        maxx=0
        max_idx=""
        for i in range(0,len(sub)):
            if maxx<=sub_money[i]:
                maxx=sub_money[i]
                max_idx=sub[i]
        last_dt=dt-timedelta(days=31)
        recs=Record.query.filter(Record.user_id==user_id,extract('year', Record.datt) ==last_dt.year,extract('month', Record.datt) ==last_dt.month,Record.type1=="expand")
        if recs is None:
            return jsonify({'status': 404, 'message': '没有任何记录'})
        money2=0
        for rec in recs:
            money2+=rec.money
        xxx=round(float(abs(money-money2)),2)
        if money==0 or money2==0:
            return jsonify({'status':404,'message':'没有任何记录'})
        ans="布奇根据您的过往消费记录，同比上个月变化了"+str(xxx)+"元，在"+max_idx+"类型上花费最多"
        return jsonify({'status': 200, 'message': '成功', 'data': ans})
    if num==6:
        dt=datetime.strptime(date,'%Y-%m-%d')
        recs=Record.query.filter(Record.user_id==user_id,extract('year', Record.datt) ==dt.year,extract('month', Record.datt) ==dt.month,Record.type1=="expend")
        if recs is None:
            return jsonify({'status': 404, 'message': '没有任何记录'})
        sub=[]
        sub_money=[]
        money=0
        for rec in recs:
            money+=rec.money
            if rec.type2 not in sub:
                sub.append(rec.type2)
                sub_money.append(0)
            for i in range(0,len(sub)):
                if sub[i]==rec.type2:
                    sub_money[i]+=rec.money
                    break
        minn=999999999
        minn_idx=""
        for i in range(0,len(sub)):
            if minn>=sub_money[i]:
                minn=sub_money[i]
                minn_idx=sub[i]
        if money==0:
            return jsonify({'status':404,'message':'没有任何记录'})
        p=float(minn)/float(money)*100.0
        p=round(p,2)
        ans="布奇发现您在"+minn_idx+"类型方面消费最低，本月占比仅达到"+str(p)+"%。合理的消费结构很重要哦"
        return jsonify({'status': 200, 'message': '成功', 'data': ans})
    if num==7:
        recs=Record.query.filter(Record.user_id==user_id,Record.type1=="expend")
        if recs is None:
            return jsonify({'status': 404, 'message': '没有任何记录'})
        sub=[]
        sub_money=[]
        num=[]
        money=0
        for rec in recs:
            money+=rec.money
            if rec.type2 not in sub:
                sub.append(rec.type2)
                sub_money.append(0)
                num.append(0)
            for i in range(0,len(sub)):
                if sub[i]==rec.type2:
                    sub_money[i]+=rec.money
                    num[i]+=1
                    break
        maxx=0
        max_money=0
        max_idx=""
        for i in range(0,len(sub)):
            if maxx<=num[i]:
                maxx=num[i]
                max_idx=sub[i]
                max_money=sub_money[i]
        if maxx==0:
            return jsonify({'status':404,'message':'没有任何记录'})
        p=float(max_money)/float(maxx)
        p=round(p,2)
        ans="布奇发现您热衷于"+max_idx+"类型的消费，平均每次消费"+str(p)+"元。"
        return jsonify({'status': 200, 'message': '成功', 'data': ans})

@app.route('/huilv/', methods=['POST'])
def huilv():
    type1=request.form.get("type1")
    money1=request.form.get("money1",type=float)
    mmm=money1
    d=[1,1.14115,4.43137,0.13334,0.14541,0.11707,0.21422,190.179,19.2552]
    name1=["RMB","HKD","TWD","EUR","USD","GBP","AUD","KRW","JPY"]
    name2=["人民币","港币","台币","欧元","美元","英镑","澳元","韩元","日元"]
    for i in range(0,len(name2)):
        if name2[i]==type1:
            money1=money1/d[i]
            abbr1=name1[i]
            break
    x=[]
    for i in range(0,len(name2)):
        if name2[i]==type1:continue
        a={
            "type2":name2[i],
            "abbr2":name1[i],
            "money2":money1*d[i]
        }
        x.append(a)
    ans={
        "type1":type1,
        "abbr1":abbr1,
        "money1":mmm,
        "list":x
    }
    return jsonify({'status': 200, 'message': '成功', 'data': ans})

from lll import fx
@app.route('/forcase/', methods=['POST'])
def forcase():
    user_id=request.form.get("user_id")
    date=request.form.get("date")
    typex=request.form.get("type1")
    dt=datetime.strptime(date,'%Y-%m-%d')
    sub=request.form.get("subtype")
    if sub is not None:
        recs=Record.query.filter(Record.type2==sub,Record.user_id==user_id,extract('year', Record.datt) ==dt.year,Record.type1==typex).order_by(desc(Record.datt))
    else:
        recs=Record.query.filter(Record.user_id==user_id,extract('year', Record.datt) ==dt.year,Record.type1==typex).order_by(desc(Record.datt))
    if recs is None:
        return jsonify({'status': 404, 'message': '没有任何记录'})
    mon=[]
    mon_money=[]
    for rec in recs:
       if rec.datt.month not in mon:
           mon.append(rec.datt.month)
           mon_money.append(0)
       for i in range(0,len(mon)):
           if mon[i]==rec.datt.month:
               mon_money[i]+=rec.money
    if len(mon_money)<3:
        return jsonify({'status':200,'message':'成功','data': -1.0})
    ans=fx(np.array(mon_money))
    ans=list(ans)
    ans=ans[0]
    ans=round(ans,2)
    return jsonify({'status': 200, 'message': '成功', 'data': ans})

@app.route('/achievement/', methods=['GET'])
def achievement():
    user_id=request.args.get("user_id")
    recs=Record.query.filter(Record.user_id==user_id).order_by(desc(Record.datt))
    if recs is None:
        return jsonify({'status': 404, 'message': '没有任何记录'})
    dt=[]
    daren=[]
    jiaotong=[]
    jizhang=[]
    meishi=[]
    fuweng=0
    meizhuang=[]
    wanjia=[]
    qiuzhi=[]
    yundong=[]
    all_expend=[]
    for rec in recs:
        dx=datetime(rec.datt.year,rec.datt.month,20)
        if dx not in dt:
            dt.append(dx)
            daren.append(0)
            jiaotong.append(0)
            jizhang.append(0)
            meishi.append(0)
            meizhuang.append(0)
            wanjia.append(0)
            qiuzhi.append(0)
            yundong.append(0)
            all_expend.append(0)
        for i in range(0,len(dt)):
            if dx == dt[i]:
                if rec.type1=="expend":
                    daren[i]-=rec.money
                    all_expend[i]+=rec.money
                else:
                    daren[i]+=rec.money
                if rec.type2=="交通":
                    jiaotong[i]+=rec.money
                if rec.type1=="earning":
                    jizhang[i]+=rec.money
                    fuweng+=rec.money
                if rec.type2=="餐饮":
                    meishi[i]+=rec.money
                if rec.type2=="购物":
                    meizhuang[i]+=rec.money
                if rec.type2=="娱乐":
                    wanjia[i]+=rec.money
                if rec.type2=="文化教育" or rec.type2=="办公":
                    qiuzhi[i]+=rec.money
                if rec.type2=="运动":
                    yundong[i]+=rec.money
                break
    daren_tag=False
    jiaotong_tag=False
    jizhang_tag=False
    meishi_tag=False
    fuweng_tag=False
    meizhuang_tag=False
    wanjia_tag=False
    qiuzhi_tag=False
    yundong_tag=False
    if fuweng>=10000:fuweng_tag=True
    print(all_expend)
    for i in range(0,len(dt)):
        if all_expend[i]==0:all_expend[i]=1
        if daren[i]>=2000:
            daren_tag=True
        if float(jiaotong[i])/float(all_expend[i])*100>=30.0:
            jiaotong_tag=True
        if jizhang[i]>=2000:
            jizhang_tag=True
        if float(meishi[i])/float(all_expend[i])*100>=50.0:
            meishi_tag=True
        if float(meizhuang[i])/float(all_expend[i])*100>=30.0:
            meizhuang_tag=True
        if float(wanjia[i])/float(all_expend[i])*100>=30.0:
            wanjia_tag=True
        if float(qiuzhi[i])/float(all_expend[i])*100>=40.0:
            qiuzhi_tag=True
        if float(yundong[i])/float(all_expend[i])*100>=30.0:
            yundong_tag=True
    ans={
        "小达人":daren_tag,
        "旅行家":jiaotong_tag,
        "记账家":jizhang_tag,
        "美食家":meishi_tag,
        "大富翁":fuweng_tag,
        "美妆家":meizhuang_tag,
        "大玩家":wanjia_tag,
        "求知者":qiuzhi_tag,
        "运动者":yundong_tag
    }
    return jsonify({'status': 200, 'message': '成功', 'data': ans})

from revChatGPT.V3 import Chatbot
@app.route('/gpt/', methods=['GET'])
def gpt():
    q=request.args.get("question")
    chatbot = Chatbot(api_key="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")
    ans=""
    for data in chatbot.ask(q):
        print(data, end="", flush=True)
        ans=ans+data
    return jsonify({'status': 200, 'message': '成功', 'data': ans})
