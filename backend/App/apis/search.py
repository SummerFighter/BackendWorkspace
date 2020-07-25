# coding:utf-8

from flask import request
import uuid
import datetime
import json
from App import app, db
from App.models import User, Video, VideoTag, LikesCollects, UserTag, Comments, Follow
from App.apis.utils import outVideos, outUser, serialize, HOST, parse_ymd, outVideosWithAccount


# 按标签搜索
@app.route('/returnByTag', methods=['POST', 'GET'])
def returnByTag():
    tags = request.values.getlist("tag")
    video_ids = db.session.query(VideoTag).filter(VideoTag.relevant_tag.in_(tags)).all()
    a = []
    for i in video_ids:
        a.append(i.video_id)
    tag_videos = db.session.query(Video).filter(Video.id.in_(a)).all()
    outVideo = outVideos(tag_videos)
    return {"videos": outVideo}


# 搜索用户
@app.route('/searchUser', methods=['POST', 'GET'])
def searchUser():
    username = request.values.get('username')
    users = db.session.query(User).filter(User.username.like("%"+username+"%")).all()
    out = outUser(users)
    return {"users": out}


# 关键字搜索
@app.route('/returnByKeyword', methods=['POST', 'GET'])
def returnByKeyword():
    keyword = request.values.getlist('keyword')

    for k in keyword:
        users = db.session.query(User).filter(User.username.like("%"+k+"%")).all()
        videos = db.session.query(Video).filter(Video.title.like("%"+k+"%")).all()
        videos2 = db.session.query(Video).filter(Video.info.like("%"+k+"%")).all()
        tag_video_ids = db.session.query(VideoTag).filter(VideoTag.relevant_tag.like("%"+k+"%")).all()

    a = []
    for i in tag_video_ids:
        a.append(i.video_id)
    tag_videos = db.session.query(Video).filter(Video.id.in_(a)).all()

    out1 = outUser(users)
    out2 = outVideos(tag_videos)
    out3 = outVideos(videos)
    out4 = outVideos(videos2)
    out = out2+out3+out4
    return {"users": out1, "videos": out}


# 获取推荐视频
@app.route("/getRecommendedVideo", methods=['POST', 'GET'])
def getRecommendedVideo():
    account = request.values.get("account")
    refreshNum = request.values.get('refreshNum')
    # 时间范围 前三天到现在
    start = datetime.datetime.now() + datetime.timedelta(days=-3)
    # 无登陆状态 没有用户
    if account == '0':
        # 按like_num/play_num的顺序返回
        if refreshNum is not None:
            result = db.session.query(Video).filter(Video.release_time > start).filter_by(state="审核通过") \
            .order_by(-Video.like_num / Video.play_num).offset(int(refreshNum)*5).limit(5).all()
        else:
            result =  db.session.query(Video).filter(Video.release_time > start) \
            .order_by(-Video.like_num / Video.play_num).limit(5).all()
        outList = outVideos(result)
        for r in result:
            r.play_num = r.play_num + 1
        db.session.commit()
        return {"videos": outList}
    # 有登陆状态
    else:
        likes = db.session.query(LikesCollects).filter_by(account=account, if_like=True).all()
        follows = db.session.query(Follow).filter_by(follower = account).all()
        if refreshNum is not None:
            result = db.session.query(Video).filter(Video.release_time > start).filter_by(state="审核通过") \
            .order_by(-Video.like_num / Video.play_num).offset(int(refreshNum)*5).limit(5).all()
        else:
            result = db.session.query(Video).filter(Video.release_time > start) \
            .order_by(-Video.like_num / Video.play_num).limit(5).all()

        outList = outVideosWithAccount(result, likes, follows,account)
        for r in result:
            r.play_num = r.play_num + 1
        db.session.commit()
        return {"videos": outList}


# 返回粉丝
@app.route("/myFollowers", methods=["GET", "POST"])
def myFollowers():
    me = request.values.get("account")
    users = db.session.query(Follow).filter(Follow.account == me).all()
    a = []
    for i in users:
        a.append(i.follower)
    aaa = db.session.query(User).filter(User.account.in_(a)).all()
    out = outUser(aaa)

    follower = db.session.query(Follow).filter(Follow.follower == me).all()
    b = []
    for i in follower:
        b.append(i.account)
    bbb = db.session.query(User).filter(User.account.in_(b)).all()
    out_=outUser(bbb)

    # 查询作品获赞数目最多的视频的作者
    video = db.session.query(Video).order_by(Video.like_num.desc()).limit(8).all()
    c = []
    for v in video:
        c.append(v.account)
    # 在推荐列表中并且已经关注了的
    ccc = db.session.query(User).filter(User.account.in_(c)).filter(User.account.in_(b)).all()
    ddd = []
    for i in ccc:
        temp = serialize(i)
        temp['avatarUrl'] = HOST + temp['avatarUrl']
        temp['sign'] = 1
        ddd.append(temp)

    eee = db.session.query(User).filter(User.account.notin_(b)).filter(User.account.in_(c)).all()
    for i in eee:
        temp = serialize(i)
        temp['avatarUrl'] = HOST + temp['avatarUrl']
        temp['sign'] = 0
        ddd.append(temp)

    return {"myFollowers": out, "myFollows": out_, "recommends": ddd}