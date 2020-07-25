import datetime

from flask import request
from App import app, db
from App.apis.utils import outMessage, HOST
from App.models import Message, Video, User


# 客户端主动获取消息
@app.route('/getMessage', methods=['POST', 'GET'])
def getMessage():
    account = request.values.get("account")
    result = db.session.query(Message).filter_by(account=account).order_by(Message.time.desc()).all()
    out = outMessage(result)
    # [db.session.delete(m) for m in result]
    db.session.commit()
    return {"message": out}


# 举报视频  数据库中不记录被谁举报和举报原因哦
@app.route('/reportVideo', methods=['POST', 'GET'])
def reportVideo():
    account = request.values.get("account")
    videoID = request.values.get("videoID")
    description = request.values.get("description")
    # 先改video表里的状态
    video = db.session.query(Video).filter_by(id=videoID).first()
    video.state = "被举报"
    # 再添加消息
    new_message = Message(account=video.account,
                          fromAccount="official",
                          description="你的视频被举报，原因："+description,
                          time=datetime.datetime.now(),
                          username="小麦视频官方",
                          userAvatarUrl="static/avatars/officialavatar.jpg")
    db.session.add(new_message)
    db.session.commit()
    return "ok"


# 发送消息
@app.route('/sendMessage', methods=['POST', 'GET'])
def sendMessage():
    account = request.values.get("account")
    toAccount = request.values.get("toAccount")
    description = request.values.get("description")
    user = db.session.query(User).filter_by(account=account).first()
    new_message = Message(account=toAccount,
                          fromAccount=account,
                          description=description,
                          time=datetime.datetime.now(),
                          username=user.username,
                          userAvatarUrl=user.avatarUrl)
    db.session.add(new_message)
    db.session.commit()
    return "ok"
