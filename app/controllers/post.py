#!/usr/bin/env python
# coding: utf-8

import os
import glob
import datetime
import random
import hashlib
import Image
import cgi
import web
import re
from web.net import htmlquote
from config import view, site_name
from app.helpers import session, utils, misc, email_templates
from app.models import postModel, nodeModel, users, notification

siteName = site_name
user = session.get_session()

# def displayTime(func):
#     import time
#     def calTime(*args):
#         # 记录开始时间
#         start = time.time()
#         # 回调原函数
#         result = func(*args)
#         passtime = time.time() - start
#         # 在结果输出追加计时信息
#         result = str(result) + "%s\n" %(passtime*1000)
#         # 返回结果
#         return result
#     # 返回重新装饰过的函数句柄
#     return calTime


#新建片段
class new_post:
    @session.login_required
    def GET(self, arg):
        per = users.get_permission_by_douid(user.douban_id)
        rights = per[0].rights
        if rights > 0: #权限判断
            node = nodeModel.getNodeByNodeId(arg)
            if node:
                return view.base(view.post_new(arg, node, user), user, siteName, rights, ntf_list=None, notification_num=None, ntf_posts=None, ntf_users=None)
            else:
                raise web.notfound()
        else:
            raise web.notfound()

    @session.login_required
    def POST(self, arg):
        data = web.input()
        postImage = data.post_Img
        postTitle = data.post_Name
        postCaption = data.post_Caption
        postArticle = data.post_Article
        postAuthor = user.id
        postTemp = data.temp
        nodeId = data.nodeID

        #入库
        postModel.newPost(postImage, postTitle, postCaption, postArticle, postAuthor, postTemp, nodeId)
        #得到最新创建的post
        thisPost = postModel.getThisPostByUserId(postAuthor)

        node = nodeModel.getNodeByNodeId(nodeId)
        nodeAuthor = users.get_user_by_id(node.node_author)
        #判断是不是在自己创建的话题中发布片段
        if nodeAuthor.id != int(postAuthor):
            #如果开启了邮件提醒，给此片段所属话题的作者发送邮件
            person = users.get_profile_by_user_id(node.node_author)
            if person.has_key('email_subscribe') and person.email_subscribe == 1 and nodeAuthor.email:
                email_templates.someone_creat_new_post(user, nodeAuthor, node, thisPost)

                print '=== email send =='
            
            #插入提醒
            notification.new_notification(node.node_author, user.id, thisPost.id, nodeId, tp=4)

        return '{"post_id":'+ str(thisPost.id)+ ',"status":"y"}'

#添加片段图片
class post_image_upload:
    @session.login_required
    def POST(self):
        # data = web.input(pic={})
        # pic = data.pic
        cgi.maxlen = 2 * 1024 * 1024 # 限制2MB
        try:
            x = web.input(uploadImg={})
            homedir = os.getcwd()
            filedir = '%s/static/upload/post_img' %homedir #图片存放路径

            if 'uploadImg' in x: # to check if the file-object is created
                filepath = x.uploadImg.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
                filename = filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension) #获取文件名
                ext = filename.split('.', -1)[-1] #获取后缀
                if ext == 'jpg' or ext == 'gif' or ext == 'jpeg' or ext == 'png' or ext == 'JPG' or ext == 'bmp' or ext == 'BMP' or ext == 'PNG':
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
                        return '{"status": "s", "info": "为了更好的显示效果，请不要上传长宽比例过大的图片"}'
                    else:
                        path = d_path + '/' + filename #for thumb
                        utils.make_post_thumb(path) #创建1200x550 / 750x230 / 365x230缩略图
                        utils.make_thumb_3(path) #创建1200x550 / 750x230 / 365x230缩略图
                        # os.remove(d_path + '/' + filename) #删除原始图片
                        p = '/static/upload/post_img/%d/%d/%d/' %(now.year, now.month, now.day) + t + '_' + authKey
                        pic_1200 = p + '_1200.jpg'
                        pic_450 = p + '_450-max.jpg'
                        pic_1201_max = p + '_1201-max.jpg'

                        # user_id = user.id
                       
                        # users.save_user_avatar(user_id, avatar)#入库
                        #session.reset()
                        return '{"status": "y", "pic_1200": "' + pic_1200 +'", "pic_450": "' + pic_450 +'", "pic_1201_max":"'+ pic_1201_max +'"}'
                else:
                    return '{"status": "s", "info": "目前只支持jpg/gif/jpeg/png/bmp格式的图片。"}'
        except ValueError:
            overflow = "o"
            return '{"status": "o", "info": "图片太大了，上传的图片不能超过2M。"}'

#删除片段图片
class post_image_delete:
    @session.login_required
    def POST(self):
        data = web.input()
        path = data.path
        part_name = data.part_name
        homedir = os.getcwd()
        imgPath = homedir + path

        if os.path.isfile(imgPath + '/.DS_Store'): 
            os.remove(imgPath + '/.DS_Store')

        files = glob.glob(imgPath + '/' + part_name + '*')

        for file in files:
            os.remove(file)
        success = "s"
        return success

#显示片段页面
class post_single:
    def GET(self, arg, ntf_type=''):
        #ntf_type为提醒类型，用来让用户从提醒页面访问片段页面时可以看到对应提醒

        post = postModel.getPostByPostId(arg)
        if post:
            post_author_info = users.get_user_by_id(post.postAuthor)
            node = nodeModel.getNodeByNodeId(post.nodeId)
            timestrf = misc.timestrf

            likers = postModel.get_voters_by_pid(post.id)
            likers_list = []
            for i in xrange(len(likers)):
                likers_list += users.get_users_by_id(likers[i].uid)

            comments = postModel.get_comments_by_pid(post.id).list()
            commenters = []
            for i in xrange(len(comments)):
                commenters += users.get_users_by_id(comments[i].uid)

            #是否登录，
            if user.is_logged:
                per = users.get_permission_by_douid(user.douban_id)
                rights = per[0].rights
                #是否投过票
                is_voted = postModel.is_voted(arg, user.id)
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

                #获取提醒页面传过来的提醒类型参数
                ntf_type = web.input(ntf_type='').ntf_type

                ntf_list = ntf_list + mtf_list
                ntf_posts = ntf_posts + mtf_posts
                ntf_users = ntf_users + mtf_users
                notification_num = notification_num+mention_num


            else:
                rights = 0
                is_voted = None
                notification_results = None
                notification_num = None
                ntf_list = None
                ntf_posts = None
                ntf_users = None

            return view.base(view.post_single(rights, node, post, post_author_info, user, timestrf, likers_list, comments, commenters, ntf_type, is_voted, misc), user, siteName, rights, ntf_list, notification_num, ntf_posts, ntf_users)
        else:
            raise web.notfound()

#更新片段图片
class post_image_update:
    @session.login_required
    def POST(self, arg):
        data = web.input()
        pid = arg
        path = data.path
        # 判断user的身份，是不是作者
        if postModel.getPostByPostId(pid).postAuthor == user.id:
            postModel.post_update(pid, postImage=path)
            success = "s"
            return success

#更新片段标题
class post_title_update:
    @session.login_required
    def POST(self,arg):
        data = web.input()
        post_Name = data.post_Name
        id = arg
        #note : 需要判断user的身份，是不是作者
        postModel.post_update(id, postTitle = post_Name)
        return '{"status": "y", "info": "标题更新成功"}'

#更新片段摘要/正文
class post_field_update:
    @session.login_required
    def POST(self,arg):
        data = web.input()
        #note : 需要判断user的身份，是不是作者
        postCaption = data.post_Caption
        postArticle = data.post_Article
        # postArticle = htmlquote(postArticle).strip().replace("\r\n", "<br/>")
        # postArticle = htmlquote(postArticle).strip()
        id = arg
        postModel.post_update(id, postCaption = postCaption, postArticle=postArticle)
        return '{"status": "y", "info": "更新成功"}'

#投票
class post_vote:
    @session.login_required
    def POST(self):
        #note 需要判断数据库中用户是不是已经投过票了。
        data = web.input()
        id = data.post_id
        uid = user.id #当前用户id
        p = postModel.getPostByPostId(id) #得到目标post
        magnitude = int(p.magnitude) #得到post的实际投票数
        ts = p.creation_ts #得到post的创建时间
        delta = (datetime.datetime.now() - ts).days #得到创建时间距今多少天

        postModel.post_update(id, magnitude = magnitude + 1) #给post的实际投票数+1, 保存最终得票数

        score = magnitude / (delta + 2)**2.1 #算出最终得票数

        postModel.post_update(id, score = score) #入库
        postModel.addVoteUser(id, uid) #记录片段ID和投票的用户ID/时间
        #插入提醒 判断是不是自己喜欢自己的
        if p.postAuthor != int(uid):
            notification.new_notification(p.postAuthor, uid, id, p.nodeId, tp=2)

            #如果开启了邮件提醒，给作者发送邮件
            author = users.get_user_by_id(p.postAuthor)

            person = users.get_profile_by_user_id(p.postAuthor)
            if person.has_key('email_subscribe') and person.email_subscribe == 1 and author.email:
                email_templates.someone_like_ur_post(user, author, p)
                print '=== email send =='

        return '{"status": "y", "info": "投票成功"}'

#取消投票
class vote_cancel(object):
    @session.login_required
    def POST(self):
        data = web.input()
        id = data.post_id
        uid = user.id
        p = postModel.getPostByPostId(id)
        magnitude = int(p.magnitude)
        ts = p.creation_ts
        delta = (datetime.datetime.now() - ts).days
        postModel.post_update(id, magnitude = magnitude - 1)
        score = magnitude / (delta + 2)**2.1
        postModel.post_update(id, score = score) #更新最终的票数
        postModel.delVoteUser(id, uid) #删除片段ID和投票的用户ID/时间
        return '{"status": "y", "info": "已取消投票"}'


#全部片段
class post_latest:
    @session.login_required
    def GET(self):
        per = users.get_permission_by_douid(user.douban_id)
        rights = per[0].rights
        postList = postModel.getRecent20Posts()
        return view.base(view.post_latest(postList), user, siteName, rights, ntf_list=None, notification_num=None, ntf_posts=None, ntf_users=None)

#添加评论
class new_post_comment:
    @session.login_required
    def POST(self, pid):
        data = web.input()
        uid = user.id
        aid = data.aid #note : 需要改成在后端通过pid得到aid,不能从前端传过来
        p = postModel.getPostByPostId(pid) #得到目标post

        reg_regchar = '@([a-zA-Z0-9][\w\-\.\_]+)'
        comment = data.postComment
        comment = htmlquote(comment).strip().replace("\r\n", "<br/>")
        usernames = re.findall(reg_regchar, comment)
        nicknames = []
        nickname_list = []
        mid_list = []

        # @提醒
        for i in xrange(len(usernames)):
            if not users.is_username_available(usernames[i]):
                nicknames += users.get_user_by_username(usernames[i]).nickname.replace(' ', '&nbsp;').split()
                comment = comment.replace('@'+ usernames[i], '@<a href="/member/'+ usernames[i] +'">' + nicknames[i] + '</a>')
                #得到@的用户id 以|分割组成字符串
                mid_list += str(users.get_user_by_username(usernames[i]).id).split()
                #去重
                mid_list = sorted(set(mid_list),key=mid_list.index)
                #以字符串形势保存@到的uid，以|分割
                # mention_id_list = '|'.join(mid_list)
            else:
                nicknames += usernames[i].split()
                comment = comment.replace('@'+ usernames[i], '@' + nicknames[i])

        # @提醒
        for mid in mid_list:
            if int(mid) !=  int(aid):
                notification.new_mention_notification(pid, p.nodeId, aid, uid,mid)
        
        print '=======notification send====='

        # 评论提醒 tp=1 表示是评论类型的提醒 同时判断是不是本人评论本人
        #这里很奇怪，不能直接判断aid 和 uid 是否相等，必须转成int
        if int(aid) != int(uid):

            notification.new_notification(aid, uid, pid, p.nodeId, tp=1)

            #如果开启了邮件提醒，给作者发送邮件
            author = users.get_user_by_id(aid)
            person = users.get_profile_by_user_id(aid)
            p = postModel.getPostByPostId(pid) #得到目标post
            if person.has_key('email_subscribe') and person.email_subscribe == 1 and author.email:
                email_templates.someone_comment_ur_post(user, author, p)
                print '=== email send =='

        postModel.add_post_comment(comment, uid, pid)
        #得到刚刚添加的comment的id,返回ajax给li添加id 供删除用
        last_comment = postModel.get_just_added_comment(uid, pid).id

        return '{"status": "y", "comment_id": "'+ str(last_comment) +'"}'

#删除评论
class del_post_comment:
    @session.login_required
    def POST(self):
        data = web.input()
        id = data.id #note : 需要判断用户是不是自己
        uid = user.id
        pid = data.pid
        postModel.delete_comment_by_comment_id(id, uid, pid)
        s = 's'
        return s


