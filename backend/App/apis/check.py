import datetime
import json

from App import db, app
from flask import render_template, request, redirect, url_for

from App.apis.utils import outVideos, outUser
from App.models import Video, User, Message


@app.route('/', methods=['GET', 'POST'])
def Welcome():
    return render_template('tourist.html')


# 审核页面
@app.route('/checkPage', methods=['GET', 'POST'])
def checkPage():
    context = {
        'videos': Video.query.all()
    }
    return render_template('videocheck.html', **context)


# 用户管理
@app.route('/usermanage', methods=['POST', 'GET'])
def usermanage():
    result = db.session.query(User).all()
    outList = outUser(result)
    awsl = []
    for i in outList:
        temp = (i['account'], i['username'], i['area'], i['gender'], i['birth'], i['school'])
        awsl.append(temp)
    content = tuple(awsl)
    labels = ('account','username','area','gender','birth','school')
    return render_template('usermanage.html', labels=labels, content=content)


# 管理员登陆
@app.route('/managerlogin', methods=['POST', 'GET'])
def managerlogin():
    account = request.args.get("account")
    password = request.args.get("password")
    if account is not None:
        if account == "summer_wheat":
            if password == "000000":
                return redirect(url_for('checkPage'))
            return "你是假的管理员吧"
        else:
            return "你不是管理员吧"
    else:
        return render_template('managerlogin.html')


# 审核通过
@app.route('/checkOK', methods=['POST', 'GET'])
def checkOK():
    videoID = request.args.get("id")
    video = db.session.query(Video).filter_by(id=videoID).first()
    video.state = "审核通过"
    new_message = Message(account=video.account,
                          fromAccount="official",
                          description="你的视频（标题："+video.title+"）已审核通过",
                          time=datetime.datetime.now(),
                          username="小麦视频官方",
                          userAvatarUrl="static/avatars/officialavatar.jpg")
    db.session.add(new_message)
    db.session.commit()
    return redirect(url_for('checkPage'))


@app.route('/checkFail',methods=['POST','GET'])
def checkFail():
    videoID = request.args.get("id")
    description = request.args.get("description")
    video = db.session.query(Video).filter_by(id=videoID).first()
    video.state = "审核不通过"
    new_message = Message(account=video.account,
                          fromAccount="official",
                          description="你的视频（标题："+video.title+"）审核未通过，原因："+description,
                          time=datetime.datetime.now(),
                          username="小麦视频官方",
                          userAvatarUrl="static/avatars/officialavatar.jpg")
    db.session.add(new_message)
    db.session.commit()
    return redirect(url_for('checkPage'))


@app.route('/reportedVideos',methods=['POST','GET'])
def reportedVideos():
    context = {
        'videos': Video.query.filter_by(state="被举报").all()
    }
    return render_template('reported.html', **context)

