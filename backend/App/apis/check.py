import json

from App import db, app
from flask import render_template


from App.apis.utils import outVideos, outUser
from App.models import Video, User


@app.route('/', methods=['GET', 'POST'])
def Welcome():
    return render_template('welcome.html')


# 审核页面
@app.route('/checkPage', methods=['GET', 'POST'])
def checkPage():

    result = db.session.query(Video).all()
    outList = outVideos(result)
    awsl = []
    for i in outList:
        temp = (i["id"], i['url'], i["title"], i['info'], i['release_time'], i['account'])
        awsl.append(temp)
    content = tuple(awsl)
    labels = ('id', 'url', 'title', 'info', 'release_time', 'account')
    return render_template('check.html', content=content,labels=labels)


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