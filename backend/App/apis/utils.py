HOST = "47.104.232.108/"


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
        temp = serialize(i)
        temp['url'] = realUrl
        temp['release_time'] = temp['release_time'].strftime('%Y-%m-%d %H: %M: %S')
        outList.append(temp)
    return outList


def outComments(result):
    outList=[]
    for i in result:
        temp = serialize(i)
        outList.append(temp)
    return outList
