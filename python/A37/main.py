from model import User,app,db
from user import user_api
from record import record_api
from achievement import achievement_api
from yuyin import yuyin_api
from piliang import piliang_api
app.register_blueprint(user_api)
app.register_blueprint(record_api)
app.register_blueprint(achievement_api)
app.register_blueprint(piliang_api)
app.register_blueprint(yuyin_api)
if __name__ == '__main__':
    # 删除所有继承自db.Model的表
    #db.drop_all()
    # 创建所有继承自db.Model的表
    #db.create_all()
    app.run(host="0.0.0.0", port=80, debug=True)
