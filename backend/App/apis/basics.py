# coding:utf-8

from flask import request
import uuid
import datetime
import json
from App import app, db
from App.models import User, Video, VideoTag, LikesCollects, UserTag, Comments, Follow
from App.apis.utils import outVideos, outComments, serialize, HOST, parse_ymd


@app.route('/')
def hello_world():
    return 'Summer Video 服务器正常运行'


# 用户注册
@app.route('/register', methods=["POST","GET"])
def register():
    account = request.values.get("account")
    password = request.values.get("password")
    username = request.values.get("username")
    user = db.session.query(User).filter_by(account=account).first()
    if user is None:
        user = User(account=account, password=password, username=username, balance=0)
        db.session.add(user)
        db.session.commit()
        return {"result": 4}
    else:
        return {"result": 5}


# 修改信息
@app.route('/setUserInfo',methods=['POST', 'GET'])
def setUserInfo():
    account = request.values.get("account")
    username = request.values.get("username")
    school = request.values.get("school")
    gender = request.values.get("gender")
    area = request.values.get("area")
    birth = request.values.get("birth")
    user = db.session.query(User).filter_by(account=account).first()
    user.username = username
    user.area = area
    user.school = school
    user.gender = gender
    user.birth = parse_ymd(birth)
    db.session.commit()
    return {"result": 6}


# 登陆
@app.route('/login', methods=["POST","GET"])
def login():
    account = request.values.get("account")
    password = request.values.get("password")
    user = db.session.query(User).filter_by(account=account).first()
    if user is not None:
        if user.password == password:
            return {"result": 1}
        else:
            return {"result": 2}
    else:
        return {"result": 3}


# 上传视频
@app.route('/upload', methods=['POST',"GET"])
def upload():
    # 从前端获取的各种参数
    file = request.files['video']
    cover = request.files['cover']
    title = request.values.get("videoTitle")
    info = request.values.get("videoInfo")
    account = request.values.get("account")
    tags = request.values.getlist("videoTag")
    # 自动生成的参数
    video_id = str(uuid.uuid4())
    release_time = datetime.datetime.now()
    url = 'static/videos/'+video_id+".mp4"
    cover_url = 'static/covers/'+video_id+".jpg"
    # video表的操作
    new_video = Video(id=video_id, title=title, url=url, info=info, release_time=release_time, account=account,cover_url=cover_url)
    db.session.add(new_video)
    db.session.commit()
    # video_tag表的操作
    for i in tags:
        videoTag = VideoTag(video_id=video_id, relevant_tag=i)
        db.session.add(videoTag)
        db.session.commit()
    # 文件写入磁盘
    file.save("App/static/videos/"+video_id+".mp4")
    cover.save("App/static/covers/"+video_id+".jpg")
    # 将结果返回客户端
    return {"result": 7}


# 视频点赞和取消点赞
@app.route("/getALike", methods=['POST','GET'])
def likeAndDislike():
    flag = request.values.get("flag")
    account = request.values.get("account")
    videoID = request.values.get("videoID")
    # 取消点赞
    if flag == '0':
        # video表中视频点赞数操作
        video = db.session.query(Video).filter_by(id=videoID).first()
        video.like_num = video.like_num-1
        # user_video_list表中的操作
        lc = db.session.query(LikesCollects).filter_by(account=account, video_id=videoID).first()
        if lc is not None:
            lc.if_like = False
        else:
            lc = LikesCollects(account=account, video_id=videoID, if_like=False)
            db.session.add(lc)
    else:  # 点赞
        video = db.session.query(Video).filter_by(id=videoID).first()
        video.like_num = video.like_num + 1

        lc = db.session.query(LikesCollects).filter_by(account=account, video_id=videoID).first()
        if lc is not None:
            lc.if_like = True
        else:
            lc = LikesCollects(account=account, video_id=videoID, if_like=True, like_time=datetime.datetime.now())
            db.session.add(lc)
    db.session.commit()
    return "ok"


# 设置用户标签
@app.route("/setUserTag", methods=["POST",'GET'])
def setUserTag():
    account = request.values.get("account")
    tags = request.values.getlist("favoriteTag")
    for i in tags:
        userTag = UserTag(account=account, favorite_tag=i)
        db.session.add(userTag)
        db.session.commit()
    return "ok"


# 评论视频
@app.route("/setComment", methods=['POST','GET'])
def setComment():
    account = request.values.get("account")
    videoID = request.values.get("videoID")
    content = request.values.get("content")
    upper_id = request.values.get("upper_id")
    cid = str(uuid.uuid4())
    comment = Comments(id=cid, account=account, video_id=videoID, content=content, head_comment_id=upper_id,release_time=datetime.datetime.now())
    db.session.add(comment)
    db.session.commit()
    return {"msg": "ok", "comment_id": cid}


# 获取某视频评论树
@app.route("/videoComments", methods=['POST','GET'])
def videoComments():
    videoID = request.values.get("videoID")
    comments = db.session.query(Comments).filter_by(video_id=videoID).all()
    outList = outComments(comments)
    return {"comment": outList}


# 获取全部视频 测试用
@app.route("/getAllVideos", methods=['POST','GET'])
def getAllVideos():
    result = db.session.query(Video).all()
    outList = outVideos(result)
    return {"videos": outList}


@app.route("/follow", methods=['POST', 'GET'])
def follow():
    flag = request.values.get("flag")
    account = request.values.get("toFollow")
    follower = request.values.get("account")
    if flag == '1':
        f = Follow(account=account, follower=follower)
        db.session.add(f)
        db.session.commit()
        return "ok"
    else:
        f = db.session.query(Follow).filter_by(account=account, follower=follower).first()
        db.session.delete(f)
        db.session.commit()
        return "ok"


# TODO 还没有排序
@app.route("/userNew", methods=['POST', 'GET'])
def userNew():
    account = request.values.get("account")
    # 时间范围 半年前到现在
    start = datetime.datetime.now() + datetime.timedelta(days=-150)
    likeVideo = db.session.query(LikesCollects).filter_by(account=account, if_like=1) \
        .filter(LikesCollects.like_time > start).all()
    uploadVideo = db.session.query(Video).filter_by(account=account) \
        .filter(Video.release_time > start).all()
    comment = db.session.query(Comments).filter_by(account=account) \
        .filter(LikesCollects.like_time > start).all()

    idList = []
    for i in likeVideo:
        idList.append(i.video_id)

    videos = db.session.query(Video).filter(Video.id.in_(idList)).all()

    outLikeVideo = outVideos(videos)
    outUpLoadVideo = outVideos(uploadVideo)
    outComment = outComments(comment)

    return {"likeVideo": outLikeVideo, "uploadVideo": outUpLoadVideo, "comment": outComment}


# 只有一个file参数的上传测试
@app.route("/uploadTest",methods=['POST','GET'])
def uploadTest():
    file = request.files['file']
    video_id = str(uuid.uuid4())
    release_time = datetime.datetime.now()
    url = 'static/videos/'+video_id+'.mp4'
    new_video = Video(id=video_id,url=url,release_time = release_time, account = "ceshi")
    db.session.add(new_video)
    db.session.commit()
    file.save("App/static/videos/"+video_id+'.mp4')
    return "ok"


# 获取用户信息
@app.route("/getUserInfo",methods=["POST","GET"])
def getUserInfo():
    account = request.values.get("account")
    user = db.session.query(User).filter_by(account=account).first()
    outUser = serialize(user)
    outUser['avatarUrl'] = HOST + outUser['avatarUrl']
    return {"info": outUser}


# 修改头像
@app.route("/setAvatar", methods=["POST", "GET"])
def setAvatar():
    file = request.files['image']
    account = request.values.get("account")
    file.save("App/static/avatars/"+account+".jpg")
    user = db.session.query(User).filter_by(account=account).first()
    user.avatarUrl = "static/avatars/"+account+".jpg"
    db.session.commit()
    return {"result": 6}

