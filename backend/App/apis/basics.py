from flask import request
import uuid
import datetime
import json
from App import app, db
from App.models import User, Video, VideoTag, LikesCollects, UserTag, Comments


@app.route('/')
def hello_world():
    return '服务器正常运行'


# 用户注册
@app.route('/register', methods=["POST"])
def register():
    account = str(uuid.uuid1())
    password = request.values.get("password")
    username = request.values.get("name")
    user = User(account=account, password=password, username=username, balance=0)
    db.session.add(user)
    db.session.commit()
    return {"msg": "注册成功", "account": account}


# 登陆
@app.route('/login', methods=["POST"])
def login():
    account = request.values.get("account")
    password = request.values.get("password")
    user = db.session.query(User).filter_by(account=account).first()
    if user is not None:
        if user.password == password:
            return {"msg": "登陆成功"}
        else:
            return {"msg": "密码错误"}
    else:
        return {"msg": "账户不存在"}


# 上传视频
@app.route('/upload', methods=['POST', 'GET'])
def upload():
    # 从前端获取的各种参数
    file = request.files['video']
    title = request.values.get("videoTitle")
    info = request.values.get("videoInfo")
    account = request.values.get("account")
    tags = request.values.getlist("videoTag")
    # 自动生成的参数
    video_id = str(uuid.uuid4())
    release_time = datetime.datetime.now()
    url = 'static/videos/'+video_id+".mp4"
    # video表的操作
    new_video = Video(id=video_id, title=title, url=url, info=info, release_time=release_time, account=account)
    db.session.add(new_video)
    db.session.commit()
    # video_tag表的操作
    for i in tags:
        videoTag = VideoTag(video_id=video_id, relevant_tag=i)
        db.session.add(videoTag)
        db.session.commit()
    # 文件写入磁盘
    file.save("App/"+url)
    # 将结果返回客户端
    resp = {"msg": "upload ok"}
    return json.dumps(resp)


# 视频点赞和取消点赞
@app.route("/getALike", methods=['POST'])
def likeAndDislike():
    flag = request.values.get("flag")
    account = request.values.get("account")
    videoID = request.values.get("videoID")
    # 取消点赞
    if flag == 0:
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
            lc = LikesCollects(account=account, video_id=videoID, if_like=True)
            db.session.add(lc)
    db.session.commit()
    return {"msg": "操作成功"}


# 视频收藏
@app.route("/getCollected",methods=['POST'])
def getCollected():
    flag = request.values.get("flag")
    account = request.values.get("account")
    videoID = request.values.get("videoID")
    # 取消收藏
    if flag == 0:
        # user_video_list表中的操作
        lc = db.session.query(LikesCollects).filter_by(account=account, video_id=videoID).first()
        if lc is not None:
            lc.if_collected = False
        else:
            lc = LikesCollects(account=account, video_id=videoID, if_collected=False)
            db.session.add(lc)
    else:  # 点赞

        lc = db.session.query(LikesCollects).filter_by(account=account, video_id=videoID).first()
        if lc is not None:
            lc.if_collected = True
        else:
            lc = LikesCollects(account=account, video_id=videoID, if_collected=True)
            db.session.add(lc)
    db.session.commit()
    return {"msg": "操作成功"}


# 设置用户标签 TODO：重复内容不能识别可能产生冗余
@app.route("/setUserTag", methods=["POST"])
def setUserTag():
    account = request.values.get("account")
    tags = request.values.getlist("favoriteTag")
    for i in tags:
        userTag = UserTag(account=account, favorite_tag=i)
        db.session.add(userTag)
        db.session.commit()

    return {"msg": "设置成功"}


# 评论视频
@app.route("/setComment", methods=['POST'])
def setComment():
    account = request.values.get("account")
    videoID = request.values.get("videoID")
    content = request.values.get("content")
    upper_id = request.values.get("upper_id")
    cid = str(uuid.uuid4())
    comment = Comments(id=cid, account=account, video_id=videoID, content=content, head_comment_id=upper_id)
    db.session.add(comment)
    db.session.commit()
    return {"msg": "评论成功"}


# 获取推荐视频 TODO 还没完
@app.route("/getRecommendedVideo", methods=['GET'])
def getRecommendedVideo():
    account = request.values.get("account")
    # 无登陆状态 没有用户
    if account is None:
        # 时间范围 前一天到现在
        start = datetime.datetime.now() + datetime.timedelta(days=-1)
        # 按like_num/play_num的顺序返回
        result = db.session.query(Video).filter(Video.release_time > start) \
            .order_by(-Video.like_num / Video.play_num).limit(10).all()

        return result