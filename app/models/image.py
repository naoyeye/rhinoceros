#!/usr/bin/env python
# coding: utf-8

import web
from config import db

def AddImage(paths, names, userID):
    #todo 判断图片是否已经存在,防止重复提交
    for i in xrange(len(paths)):
        db.insert('image', path = paths[i], imageTitle = names[i],  userID = userID)

def saveTitleDescribe(imagePath, imageTitle, imageDescribe):
    for i in xrange(len(imagePath)):
        db.update('image', vars=dict(path=imagePath[i]), where='path = $path', imageDescribe=imageDescribe[i].strip().replace("\r\n", " "), imageTitle=imageTitle[i]) #这个imageDescribe需要替换回车，花了我好多时间才知道怎么替换

#todo ----可以合并的 ----
#通过用户id得到用户上传的图片路径
def get_paths_by_id(userID):
    return db.select('image', order='id DESC', vars=dict(userID=userID), where='userID = $userID', what='path')

#通过用户id得到用户上传的图片id
def get_imageID_by_id(userID):
    return db.select('image', order='id DESC', vars=dict(userID=userID), where='userID = $userID', what='id')

#通过用户id得到用户上传的图片
def get_img_by_id(userID):
    return db.select('image', order='id DESC', vars=dict(userID=userID), where='userID = $userID')

#通过用户id得到用户上传的图片id (单个id)
def get_img_by_imgid(img_id):
    return web.listget(
        db.select('image', vars=dict(id=img_id), 
            where='id = $id'), 0, {})

#通过图片id得到用户上传的图片 (多个id)
def get_imgs_by_imgid(img_id):
    return db.select('image', vars=dict(id=img_id), where='id = $id')

#得到最近上传的10张图片
def get_last_image():
    return db.select('image', limit = 10, order='id DESC')

#浏览数加1
def add_img_hit(id):
    db.query("UPDATE image set view_num=view_num+1 WHERE id=$id", vars=dict(id=id))

#判断图片的用户浏览记录表中是否已存在记录
def user_not_viewed_image(user_id, image_id):
    return not db.select(
        'ImageViewUsers', 
        vars = dict(user_id=user_id, image_id=image_id),
        what = 'count(id) as c', 
        where = 'user_id = $user_id and image_id = $image_id')[0].c

#新增浏览记录
def add_user_to_img_viewed(user_id, image_id):
    db.insert('ImageViewUsers', user_id = user_id, image_id = image_id)


#更新图片标题和描述信息
def UpdateImageTitleAndDescribe(imageId, imageTitle, imageDescribe):
    db.update('image', vars=dict(id=imageId), where='id = $id', imageDescribe=imageDescribe, imageTitle=imageTitle)

#删除图片
def DeleteImageByImageID(imageId, userID):
    db.delete('image', vars = dict(id=imageId, userID=userID), where = 'id = $id and userID = $userID')
    # 喜欢表里的也要做处理，要不然列出用户喜欢的图片时会有问题
    db.delete('ImageFavorite', vars = dict(img_id=imageId), where = 'img_id = $img_id')

#喜欢某图片
def AddFavorite(u_id, i_id):
    db.insert('ImageFavorite', user_id = u_id, img_id = i_id)
    #同时更新image里的‘favo_num’字段
    db.query("UPDATE image set favo_num=favo_num+1 WHERE id=$id", vars=dict(id=i_id))

#取消喜欢
def CancelFavorite(u_id, i_id):
    db.delete('ImageFavorite', vars = dict(img_id=i_id, user_id = u_id), where = 'img_id = $img_id and user_id = $user_id')
    #同时删除image里的‘favo_num’字段
    db.query("UPDATE image set favo_num=favo_num-1 WHERE id=$id", vars=dict(id=i_id))

#是否喜欢当前图片
def IsFavorite(u_id, i_id):
    user_id = u_id
    img_id = i_id
    return db.select(
        'ImageFavorite', 
        vars = dict(img_id=img_id, user_id=user_id),
        what = 'count(id) as c', 
        where = 'img_id = $img_id and user_id = $user_id')[0].c

#得到用户喜欢的图片id
def GetFavImageByUserId(u_id):
    return db.select('ImageFavorite', vars=dict(user_id=u_id), where='user_id = $user_id')

#图片被多少用户喜欢
def GetFavImageByImageId(img_id):
    return db.select('ImageFavorite', vars=dict(img_id=img_id),  order='id DESC', where='img_id = $img_id')

#用户喜欢了多少图片
def GetUserFavCount(user_id):
    return int(db.select('ImageFavorite', what='count(distinct id) as c', vars=dict(user_id=user_id), where='user_id = $user_id')[0].c)

#分页用
def query(userID):
    results = db.select('image', order='id DESC', vars=dict(userID=userID), where='userID = $userID')
    count = int(db.select('image', what='count(distinct id) as c', vars=dict(userID=userID), where='userID = $userID')[0].c)
    return (results, count)

#添加图片评论
def add_img_comment(comment, u_id, i_id):
    db.insert('ImageComments', user_id = u_id, image_id = i_id, comment = comment)
    #同时更新image里的‘comm_num’字段
    db.query("UPDATE image set comm_num=comm_num+1 WHERE id=$id", vars=dict(id=i_id))

#删除图片评论
def DeleteCommentByCommentID(id, user_id, img_id):
    db.delete('ImageComments', vars = dict(id=id, user_id = user_id), where = 'id = $id and user_id = $user_id')
    db.query("UPDATE image set comm_num=comm_num-1 WHERE id=$id", vars=dict(id=img_id))

#得到某张图片的评论
def get_comment_by_image_id(id):
    return db.select('ImageComments', vars=dict(image_id=id), 
            where='image_id = $image_id')

