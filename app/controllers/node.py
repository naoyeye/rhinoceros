#!/usr/bin/env python
# coding: utf-8

import os
import datetime
import random
import hashlib
import Image
import cgi
import web
import re
from web.net import htmlquote
from config import view, site_name
from app.helpers import session, utils, misc
from app.models import nodeModel, postModel, users, notification

siteName = site_name
user = session.get_session()


#新建话题节点
class new_node:
    @session.login_required
    def GET(self):
        per = users.get_permission_by_douid(user.douban_id)
        rights = per[0].rights
        if rights > 0: #权限判断
            return view.base(view.node_new(), user, siteName, rights, ntf_list=None, notification_num=None, ntf_posts=None, ntf_users=None)
        else:
            raise web.notfound()

    @session.login_required
    def POST(self):
        data = web.input(node_Open=[])
        nodeImg = data.node_Img
        nodeName = data.node_Name
        nodeDesc = data.node_Desc
        # nodeOpen = data.node_Open #note: 暂时全部开放
        nodeOpen = 1
        nodeCreater = user.id

        nodeModel.newNode(nodeImg, nodeName, nodeDesc, nodeOpen, nodeCreater)
        thisNode = nodeModel.getThisNodeByUserId(nodeCreater)
        return '{"node_id":"'+ str(thisNode.id)+ '", "status":"y"}'#返回刚刚创建的话题节点ID 供AJAX跳转

        
#上传话题节点图片
class node_image():
    @session.login_required
    def POST(self):
        cgi.maxlen = 2 * 1024 * 1024 # 限制2MB
        try:
            x = web.input(uploadImg={})
            homedir = os.getcwd()
            filedir = '%s/static/upload/node_img' %homedir #图片存放路径

            if 'uploadImg' in x: # to check if the file-object is created
                filepath = x.uploadImg.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
                filename = filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension) #获取文件名
                ext = filename.split('.', -1)[-1] #获取后缀
                if ext == 'jpg' or ext == 'gif' or ext == 'jpeg' or ext == 'png' or ext == 'JPG':
                    now = datetime.datetime.now()
                    
                    d_path = filedir + '/%d/%d/%d' %(now.year, now.month, now.day)
                    if not os.path.exists(d_path):
                        os.makedirs(d_path) #创建当前日期目录

                    t = '%d%d%d%d%d%d' %(now.year, now.month, now.day, now.hour, now.minute, now.second)                    
                    all = list('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSQUVWXYZ')
                    randStr = ''
                    for i in range(10):
                        index = random.randint(0,len(all)-1)
                        randStr = randStr + all[index] #生成10位随机数
                    authKey = hashlib.md5(randStr + user.username).hexdigest()
                    filename = t + '_' + authKey + '.' + ext #以时间+authKey作为文件名
                    
                    fout = open(d_path + '/' + filename,'wb') # creates the file where the uploaded file should be stored
                    fout.write(x.uploadImg.file.read()) # writes the uploaded file to the newly created file.
                    fout.close() # closes the file, upload complete.

                    im = Image.open(d_path + '/' + filename)
                    width, height = im.size #判断比例
                    if width/height > 5 or height/width > 5 :
                        os.remove(d_path + '/' + filename) #删除图片
                        scale = "s"
                        return scale
                    else:
                        path = d_path + '/' + filename #for thumb
                        utils.make_node_thumb(path) #创建75x75缩略图
                        os.remove(d_path + '/' + filename) #删除原始图片
                        mid_src = '/static/upload/node_img/%d/%d/%d/' %(now.year, now.month, now.day) + t + '_' + authKey + '_75.jpg'

                        # user_id = user.id
                       
                        # users.save_user_avatar(user_id, avatar)#入库
                        #session.reset()
                        return mid_src

                else:
                    return '上传格式仅支持jpg/png/gif/jpeg'

        except ValueError:
            overflow = "o"
            return overflow

#ajax 删除话题节点图片
class delete_node_image:
    @session.login_required
    def POST(self):
        s = web.input()
        x = s.d
        nid = s.nid
        #安全起见，判断是不是话题作者本人
        if nid != 'new' and user.id == nodeModel.getNodeByNodeId(nid).node_author:

            #删除硬盘中的图片文件
            homedir = os.getcwd()
            imgPath = homedir + x
            os.remove(imgPath)
            nodeImg = imgPath
            print 'Image Deleted'

            #更新数据库
            nodeModel.nodeUpdate(nid, nodeImg=None)
            success = "s"
            return success
        #new 是创建新话题时，那时没有nid
        elif nid == 'new':
            #更新数据库
            nodeModel.nodeUpdate(nid, nodeImg=None)
            success = "s"
            return success


#话题节点
class node_show:
    def GET(self, arg, p=1):
        node = nodeModel.getNodeByNodeId(arg)
        if node:
            timestrf = misc.timestrf
            page = int(p)
            perpage = 10
            offset = (page - 1) * perpage

            node_author_info = users.get_user_by_id(node.node_author)
            postList = postModel.getPostListByNodeIdSortByScore(arg, offset, perpage).list()

            a = []
            for post in postList:
                a += str(post.postAuthor).split()

            authors = []
            for i in xrange(len(a)):
                authors += users.get_users_by_id(a[i])

            #得到权限
            if user.is_logged:
                per = users.get_permission_by_douid(user.douban_id)
                rights = per[0].rights

                #得到提醒
                notification_results, notification_num = notification.get_unread_notification(user.id)
                #得到@提醒
                notification_mention_results, mention_num= notification.get_unread_metion_notifition(user.id)
                #链表 得到提醒的详细id\名称等
                ntf_posts = []
                ntf_users = []
                mtf_posts = []
                mtf_users = []

                ntf_list = notification_results.list()
                mtf_list = notification_mention_results.list()
                for x in xrange(len(ntf_list)):
                    ntf_posts += postModel.getPostsByPostId(ntf_list[x].pid)
                    ntf_users += users.get_users_by_id(ntf_list[x].uid)

                for x in xrange(len(mtf_list)):
                    mtf_posts += postModel.getPostsByPostId(mtf_list[x].pid)
                    mtf_users += users.get_users_by_id(mtf_list[x].uid)

                ntf_list = ntf_list + mtf_list
                ntf_posts = ntf_posts + mtf_posts
                ntf_users = ntf_users + mtf_users
                notification_num = notification_num+mention_num

            else:
                rights = 0
                notification_results = None
                notification_num = None
                ntf_list = None
                ntf_posts = None
                ntf_users = None

            return view.base(view.node_show(timestrf, rights, node, postList, node_author_info, user, authors, sort='interesting'), user, siteName, rights, ntf_list, notification_num, ntf_posts, ntf_users)
        else:
            raise web.notfound()

class node_recent:
    def GET(self,arg, p=1):
        node = nodeModel.getNodeByNodeId(arg)

        if node:
            timestrf = misc.timestrf
            page = int(p)
            perpage = 10
            offset = (page - 1) * perpage

            node_author_info = users.get_user_by_id(node.node_author)
            postList = postModel.getPostListByNodeIdSortByID(arg, offset, perpage).list()

            a = []
            for post in postList:
                a += str(post.postAuthor).split()

            authors = []
            for i in xrange(len(a)):
                authors += users.get_users_by_id(a[i])
            
            postcount = node.postMount
            pages = postcount / perpage
            # if postcount % perpage > 0:
            #     pages += 1
            # if page > pages:
            #     raise web.seeother('/')
            # else:
            if user.is_logged:
                per = users.get_permission_by_douid(user.douban_id)
                rights = per[0].rights
                #得到提醒
                notification_results, notification_num = notification.get_unread_notification(user.id)
                #得到@提醒
                notification_mention_results, mention_num= notification.get_unread_metion_notifition(user.id)
                #链表 得到提醒的详细id\名称等
                ntf_posts = []
                ntf_users = []
                mtf_posts = []
                mtf_users = []

                ntf_list = notification_results.list()
                mtf_list = notification_mention_results.list()
                for x in xrange(len(ntf_list)):
                    ntf_posts += postModel.getPostsByPostId(ntf_list[x].pid)
                    ntf_users += users.get_users_by_id(ntf_list[x].uid)

                for x in xrange(len(mtf_list)):
                    mtf_posts += postModel.getPostsByPostId(mtf_list[x].pid)
                    mtf_users += users.get_users_by_id(mtf_list[x].uid)

                ntf_list = ntf_list + mtf_list
                ntf_posts = ntf_posts + mtf_posts
                ntf_users = ntf_users + mtf_users
                notification_num = notification_num+mention_num

            else:
                rights = 0
                notification_results = None
                notification_num = None
                ntf_list = None
                ntf_posts = None
                ntf_users = None
                
            return view.base(view.node_show(timestrf, rights, node, postList, node_author_info, user, authors, sort='recent'), user, siteName, rights, ntf_list, notification_num, ntf_posts, ntf_users)
        else:
            raise web.notfound()

#话题节点瀑布流
class node_load_more:
    def GET(self, arg, page_num):
        page = int(page_num)
        perpage = 10
        offset = (page - 1) * perpage

        url = web.ctx.get('path')
        if int(url.count('recent')) == 0:
            postList = postModel.getPostListByNodeIdSortByScore(arg, offset, perpage).list()
        else:
            postList = postModel.getPostListByNodeIdSortByID(arg, offset, perpage).list()

        a = []
        for post in postList:
            a += str(post.postAuthor).split()

        authors = []
        for i in xrange(len(a)):
            authors += users.get_users_by_id(a[i])

        if int(url.count('recent')) == 0:
            return view.post_list(postList, authors)
        else:
            return view.post_list(postList, authors)


#编辑话题节点
class node_update:
    @session.login_required
    def POST(self, arg):
        data = web.input(node_Open=[])
        nodeImg = data.node_Img
        nodeName = data.node_Name
        nodeDesc = data.node_Desc
        # nodeOpen = data.node_Open #note: 暂时
        nodeOpen = 1
        # nodeCreater = user.id

        # nodeModel.nodeUpdate(arg, nodeImg, nodeName, nodeDesc, nodeOpen)
        nodeModel.nodeUpdate(arg, nodeImg=nodeImg, nodeName=nodeName, nodeDesc=nodeDesc, nodeOpen=nodeOpen)
        return '{"node_id":'+ str(arg)+ ',"status":"y"}'#

#话题列表 #仅管理员可见
class node_all(object):
    @session.login_required
    def GET(self):
        per = users.get_permission_by_douid(user.douban_id)
        rights = per[0].rights
        if rights > 1:
            nodeList = nodeModel.getLastNodes().list()
            authors = []
            for i in xrange(len(nodeList)):
                authors += users.get_users_by_id(nodeList[i].node_author)
            return view.base(view.node_all(nodeList, authors), user, siteName, rights, ntf_list=None, notification_num=None, ntf_posts=None, ntf_users=None)
        else:
            return web.notfound()
