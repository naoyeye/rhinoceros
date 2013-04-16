#!/usr/bin/env python
# coding: utf-8

import web
# import socket
from config import db
from web.net import htmlquote
from app.helpers import misc

#创建片段
def newPost(postImage, postTitle, postCaption, postArticle, postAuthor, postTemp, nodeId):
    if postImage != '':
        postImage = postImage.split('_')[0] + "_" + postImage.split('_')[1] + "_" + postImage.split('_')[2];
    
    # 过滤
    # postArticle = htmlquote(postArticle).strip()

    # postArticle = postArticle.replace("\r\n", "<br/>")

    db.insert('_post', postImage=postImage, postTitle=postTitle, postCaption=postCaption, postArticle=postArticle, postAuthor=postAuthor, postTemp=postTemp, nodeId= nodeId)
    db.query("UPDATE _node set postMount=postMount+1 WHERE id=$id", vars=dict(id=nodeId))

#得到刚创建的片段
def getThisPostByUserId(postAuthor):
    return web.listget(
        db.select('_post', vars=dict(postAuthor=postAuthor), order='id DESC',
            where='postAuthor = $postAuthor'), 0, {})

#得到某一个片段
def getPostByPostId(PostId):
    return web.listget(
        db.select('_post', vars=dict(id=PostId), where='id = $id'), 0, {})

#得到某一个片段
def getPostsByPostId(PostId):
    return db.select('_post', vars=dict(id=PostId), where='id = $id')

#得到最新20个片段
def getRecent20Posts():
    return db.select('_post', limit=20,  order='id DESC')

#得到某个话题下最新1个片段
def getRecentOnePostsInNode(nodeId):
    return web.listget(
    db.select('_post', limit=1,  order='id DESC', vars=dict(nodeId=nodeId), where='nodeId = $nodeId'), 0, {})

#得到某个用户创建的片段
def getCreatedPostsByUserId(postAuthor, offset, limit):
    return db.select('_post', order='id DESC', offset=offset, limit=limit, vars=dict(postAuthor=postAuthor), where='postAuthor = $postAuthor')

#得到某个用户喜欢的片段
def getLikedPostsByUserId(uid, offset, limit):
    return db.select('_post_vote_user', order='creation_ts DESC', offset=offset, limit=limit, vars=dict(uid=uid), where='uid = $uid')

#得到某个用户参与话题节点id
def groupGetCreatedPostsByUserId(postAuthor, offset, limit):
    return db.select('_post', order='id DESC', offset=offset, limit=limit, vars=dict(postAuthor=postAuthor), where='postAuthor = $postAuthor', group='nodeId')

#得到全部片段
def getPostsByPostId(PostId):
    return db.select('_post', vars=dict(id=PostId), where='id = $id')

#按评分排序
def getPostListByNodeIdSortByScore(NodeId, offset, perpage):
    return db.select('_post', order='score DESC, magnitude DESC, id DESC', offset=offset, limit=perpage, vars=dict(nodeId=NodeId), where='nodeId = $nodeId')

#按时间排序
def getPostListByNodeIdSortByID(NodeId, offset, perpage):
    return db.select('_post', order='id DESC', offset=offset, limit=perpage, vars=dict(nodeId=NodeId), where='nodeId = $nodeId')

# def nodeLinkPost(nodeID, postID):
#     db.insert('_nodeLinkPost', nodeID=postImage, postID=postID)

#更新片段
def post_update(id, **value):
    db.update('_post', vars=dict(id=id), where='id = $id', **value )

#增加投票
def addVoteUser(pid, uid):
    db.insert('_post_vote_user', pid = pid, uid = uid)

#取消投票
def delVoteUser(pid, uid):
    db.delete('_post_vote_user', vars = dict(pid=pid, uid = uid), where = 'pid = $pid and uid = $uid')

#得到投票数
def is_voted(pid, uid):
    return db.select(
        '_post_vote_user', 
        vars = dict(pid=pid, uid=uid),
        what = 'count(id) as c', 
        where = 'pid = $pid and uid = $uid')[0].c

#根据pid得到投票的uid
def get_voters_by_pid(pid):
    return db.select('_post_vote_user', vars=dict(pid=pid), where='pid = $pid', order='id DESC')

#添加评论
def add_post_comment(comment, uid, pid):
    comment = comment
    db.insert('_post_comments', uid = uid, pid = pid, content = comment)
    #更新post评论数
    db.query("UPDATE _post set comment_num=comment_num+1 WHERE id=$id", vars=dict(id=pid))

#得到评论
def get_comments_by_pid(pid):
    return db.select('_post_comments', vars=dict(pid=pid), where='pid = $pid', order='id ASC')

def get_just_added_comment(uid, pid):
    return web.listget(
        db.select('_post_comments', vars = dict(pid=pid, uid = uid), where='pid = $pid and uid = $uid', order='id DESC', limit = 1), 0, {})

#删除评论
def delete_comment_by_comment_id(id, uid, pid):
    db.delete('_post_comments', vars = dict(id=id, uid = uid), where = 'id = $id and uid = $uid')
    #更新post评论数
    db.query("UPDATE _post set comment_num=comment_num-1 WHERE id=$id", vars=dict(id=pid))


