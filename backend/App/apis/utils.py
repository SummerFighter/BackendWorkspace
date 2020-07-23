from datetime import datetime

from App import db
from App.models import User

HOST = "http://47.104.232.108/"


# 日期解析
def parse_ymd(s):
    year_s, mon_s, day_s = s.split('-')
    return datetime(int(year_s), int(mon_s), int(day_s))


# sqlalchemy到dist对象
def serialize(model):
    from sqlalchemy.orm import class_mapper
    columns = [c.key for c in class_mapper(model.__class__).columns]
    return dict((c, getattr(model, c)) for c in columns)


# 输出视频对象列表
def outVideos(result):
    outList = []
    for i in result:
        realUrl = HOST + i.url
        realCoverUrl = HOST+i.cover_url
        temp = serialize(i)
        temp['url'] = realUrl
        temp['cover_url'] = realCoverUrl
        temp['release_time'] = temp['release_time'].strftime('%Y-%m-%d %H: %M: %S')
        user = db.session.query(User).filter_by(account=temp['account']).first()
        temp['author_url'] = HOST+user.avatarUrl
        outList.append(temp)
    return outList


def outComments(result):
    outList=[]
    for i in result:
        temp = serialize(i)
        user = db.session.query(User).filter_by(account=temp['account']).first()
        temp['avatar_url'] = HOST + user.avatarUrl
        temp['username'] = user.username
        outList.append(temp)
    return outList


def outComment(comment):
    temp = serialize(comment)
    user = db.session.query(User).filter_by(account=temp['account']).first()
    temp['avatar_url'] = HOST + user.avatarUrl
    temp['username'] = user.username
    return temp


def outUser(result):
    outList=[]
    for i in result:
        temp = serialize(i)
        temp['avatarUrl'] = HOST+temp['avatarUrl']
        if temp['birth'] is not None:
            temp['birth'] = temp['birth'].strftime('%Y-%m-%d')
        outList.append(temp)
    return outList


def outMessage(result):
    outList = []
    for i in result:
        temp = serialize(i)
        temp['userAvatarUrl']=HOST+temp['userAvatarUrl']
        outList.append(temp)
    return outList
