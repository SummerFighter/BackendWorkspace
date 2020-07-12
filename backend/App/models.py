from sqlalchemy.orm import relationship

from App import db


# 用户
class User(db.Model):
    __tablename__ = "user"
    account = db.Column(db.String(100), primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    balance = db.Column(db.Float)
    upload_videos = relationship("Video", backref="user")  # 上传的视频列表
    tags = relationship("UserTag", backref="user")  # 用户标签


# 视频
class Video(db.Model):
    __tablename__ = "video"
    id = db.Column(db.String(200), primary_key=True)
    title = db.Column(db.String(255), unique=True)
    url = db.Column(db.String(500), unique=True)  # 相对url 根目录下的位置 其实可以不要？
    info = db.Column(db.Text)  # 视频简介
    release_time = db.Column(db.DateTime)
    play_num = db.Column(db.BigInteger, default=0)  # 播放量
    like_num = db.Column(db.BigInteger, default=0)  # 点赞量
    trans_num = db.Column(db.BigInteger, default=0)  # 转发数量
    comment_num = db.Column(db.BigInteger, default=0)  # 评论数量
    account = db.Column(db.String(100), db.ForeignKey('user.account'))  # 上传者
    tags = relationship("VideoTag", backref="video")


# 用户对视频的点赞、收藏表
class LikesCollects(db.Model):
    __tablename__ = "user_video_list"
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(100))
    video_id = db.Column(db.String(200))
    if_like = db.Column(db.Boolean, default=False)
    if_collected = db.Column(db.Boolean, default=False)


# 视频评论表
class Comments(db.Model):
    __tablename__ = "video_comment"
    id = db.Column(db.String(200), primary_key=True)
    video_id = db.Column(db.String(200))
    account = db.Column(db.String(100))
    content = db.Column(db.Text)
    head_comment_id = db.Column(db.String(200))


# 视频分析
class VideoDeep(db.Model):
    __tablename__ = "video_deep"
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(200))
    account = db.Column(db.String(100))
    stand_time = db.Column(db.Time)  # 视频停留时间
    view_time = db.Column(db.DateTime)  # 浏览时间


# 用户标签
class UserTag(db.Model):
    __tablename__ = "user_tag"
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(100), db.ForeignKey("user.account"))
    favorite_tag = db.Column(db.String(100))


# 视频标签
class VideoTag(db.Model):
    __tablename__ = "video_tag"
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(200), db.ForeignKey("video.id"))
    relevant_tag = db.Column(db.String(100))


# 当models.py直接被运行时运行，重新创建表
if __name__ == '__main__':
    db.drop_all()
    db.create_all()
