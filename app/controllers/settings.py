#!/usr/bin/env python
# coding: utf-8

import web
import config
import md5
import os
import Image
import time
import datetime
import cgi
import random
import hashlib

from web import form

from app.models import applicants, postModel, users, notification

from app.helpers import session, utils
from app.helpers import email_templates
from config import view, site_name, encryption_key


siteName = site_name

user = session.get_session()

# password_form = form.Form(
#     form.Password('password', 
#         form.notnull,
#         form.Validator('至少6个字符', 
#         lambda x: users.is_valid_password(x)),
#         description='你的新密码:'),
#     form.Button('submit', type='submit', value='Change password')
# )

# nickname_form = form.Form(
#     form.Textbox('nickname', 
#         form.notnull,
#         description='你的新昵称:'),
#     form.Button('submit', type='submit', value='Change your nickname')
# )

# vemail = form.regexp(r'.+@.+', '请检查你的邮箱格式')
# email_form = form.Form(
#     form.Textbox('email', 
#         form.notnull, vemail,
#         form.Validator('这个已经被占用了.', 
#         lambda x: users.is_email_available(x)),
#         description='你的新邮箱:'),
#     form.Button('submit', type='submit', value='Change your email')
# )

# def render_settings(nickname_form=nickname_form(), email_form=email_form(), password_form=password_form(), on_success_message=''):
#     #counts = applicants.get_counts()
#     username = str(user.username)
#     u = users.get_user_by_username(username)
#     # if not u.avatarPath:
#     #    src = '/static/public/img/default_48x48.jpg'
#     # else:
#     #    src = '/static/upload/image' + avatar + '_48.jpg'
    
    
#     return view.base(
#         view.settings(user, nickname_form, email_form, password_form, on_success_message, u), user, site_name
#     )

class index:
    @session.login_required
    def GET(self):
        # u = users.get_user_by_id(session.get_user_id())
        # ut = u.nicknameChangeTime #得到上次修改昵称的时间
        # c = datetime.datetime.now()#得到当前时间

        # if (c - ut).days < 30: #时间差
        #     can_change_nickname = False
        # else:
        #     can_change_nickname = True

        #得到权限
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

        #得到资料设置
        profile = users.get_profile_by_user_id(user.id)
        #得到邮箱验证状态
        confirm = users.get_confirm_email_by_douban_id(user.douban_id)

        return view.base(view.member_setting_profile(user, profile, confirm), user, siteName, rights, ntf_list, notification_num, ntf_posts, ntf_users)

    # @session.login_required
    # def POST(self):
    #     f = web.input()

    #     #判断是更新还是新增
    #     if users.is_user_profile_changed(session.get_user_id()):
    #         users.update_profile(session.get_user_id(), **f)
    #     else:
    #         users.insert_profile(session.get_user_id(), **f)
    #     session.reset()
    #     raise web.seeother('/settings')



# class change_nickname:
#     @session.login_required
#     def POST(self):
#         f = web.input()
#         time = datetime.datetime.now()
#         users.update(session.get_user_id(), nickname=f.nickname, nicknameChangeTime = time)
#         session.reset()

class change_email:
    # @session.login_required
    # def GET(self):
    #     e = users.get_confirm_email_by_email(user.email)
    #     c = e.get('confirmed')
    #     if c == 1:
    #         return view.base(view.member_setting_email(user, msg='<span class="label label-success">已验证</lable>'), user, siteName)
    #     else:
    #         return view.base(view.member_setting_email(user, msg='<span class="label label-important">未验证</span>'), user, siteName)

    @session.login_required
    def POST(self):
        email = web.input().email

        #检查是否变动
        old_email = users.get_user_by_id(user.id).email
        if email == old_email:
            return '{"status":"n", "code":"n-wbh", "info":"邮箱地址未变化"}'

        #检查新邮箱是否已经存在
        elif not users.is_email_available(email):
            return '{"status":"n", "code":"n-ybsy", "info":"此邮箱已被使用"}'

        else:
            #更新用户表中email字段
            # users.update(user.id, email=email)

            token = md5.md5(time.ctime() + email).hexdigest()
            t = datetime.datetime.now()
            #更新邮箱验证表中email\confirmed\token字段
            users.update_confirm_email_by_douban_id(user.douban_id, email, token, t)

            #发送通知邮件
            
            email_templates.change_email(email, token)
            print '======email send======'

            # session.reset()
            return '{"status":"y", "code":"y-y", "info":"验证邮件已发送，请通过邮件中的链接来验证此邮箱。在未验证之前，提醒通知还是发到旧邮箱中。"}'


# class change_password:
#     @session.login_required
#     def GET(self):
#         return view.base(view.member_setting_password(user), user, siteName)

#     @session.login_required
#     def POST(self):
#         data = web.input()
#         email = data.email
#         id = data.id
#         password = data.password
#         newPassword = data.newPassword

#         user = users.get_user_by_id(id)
#         ua = web.ctx.env.get('HTTP_USER_AGENT')
#         ip = web.ctx.ip
#         timestamp = time.mktime(time.localtime())
#         tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))

#         if users.is_correct_password(email, password):
#             users.update(id, password=hashlib.md5(newPassword + encryption_key).hexdigest())
#             session.reset()
#             email_templates.change_pwd(email, user, ua, ip, tm)
#             web.header('Content-Type', 'application/json')
#             return '{"status":"y"}'
#         else :
#             web.header('Content-Type', 'application/json')
#             return '{"status":"n"}'

# class member_avatar:
#     @session.login_required
#     def GET(self):
#         return view.base(view.member_setting_avatar(user, mid_src=''), user, siteName)

#     @session.login_required
#     def POST(self):
#         cgi.maxlen = 2 * 1024 * 1024 # 限制2MB
#         try:
#             x = web.input(uploadImg={})
#             homedir = os.getcwd()
#             filedir = '%s/static/upload/image' %homedir #图片存放路径

#             if 'uploadImg' in x: # to check if the file-object is created
#                 filepath = x.uploadImg.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
#                 filename = filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension) #获取文件名
#                 ext = filename.split('.', -1)[-1] #获取后缀
#                 if ext == 'jpg' or ext == 'gif' or ext == 'jpeg' or ext == 'png' or ext == 'JPG':
#                     now = datetime.datetime.now()
                    
#                     d_path = filedir + '/%d/%d/%d' %(now.year, now.month, now.day)
#                     if not os.path.exists(d_path):
#                         os.makedirs(d_path) #创建当前日期目录

#                     t = '%d%d%d%d%d%d' %(now.year, now.month, now.day, now.hour, now.minute, now.second)                    
#                     all = list('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSQUVWXYZ')
#                     randStr = ''
#                     for i in range(10):
#                         index = random.randint(0,len(all)-1)
#                         randStr = randStr + all[index] #生成10位随机数
#                     authKey = hashlib.md5(randStr + user.username).hexdigest()
#                     filename = t + '_' + authKey + '.' + ext #以时间+authKey作为文件名
                    
#                     fout = open(d_path + '/' + filename,'wb') # creates the file where the uploaded file should be stored
#                     fout.write(x.uploadImg.file.read()) # writes the uploaded file to the newly created file.
#                     fout.close() # closes the file, upload complete.

#                     im = Image.open(d_path + '/' + filename)
#                     width, height = im.size #判断比例
#                     if width/height > 5 or height/width > 5 :
#                         os.remove(d_path + '/' + filename) #删除图片
#                         #session.reset()
#                         return view.base(view.member_setting_avatar(user, mid_src='', message='图片的比例有些不太合适，请选择一张更容易辨识的图片吧'), user, siteName)
#                     else:
#                         path = d_path + '/' + filename #for thumb
#                         utils.make_thumb(path) #创建缩略图

#                         #big_src = '/static/upload/image/%d/%d/%d/' %(now.year, now.month, now.day) + filename
#                         mid_src = '/static/upload/image/%d/%d/%d/' %(now.year, now.month, now.day) + t + '_' + authKey + '_160.jpg'
#                         #sml_src = '/static/upload/image/%d/%d/%d/' %(now.year, now.month, now.day) + t + '_' + authKey + '_48x48.jpg'

#                         user_id = user.id
#                         avatar = '/%d/%d/%d/' %(now.year, now.month, now.day) + t + '_' + authKey
                       
#                         users.save_user_avatar(user_id, avatar)#入库
#                         #session.reset()
#                         return view.base(view.member_setting_avatar(user, mid_src), user, siteName)

#                 else:
#                     #session.reset()
#                     return view.base(view.member_setting_avatar(
#                         user, mid_src='',
#                         message='上传格式仅支持jpg/png/gif/jpeg'), user, siteName)
#         except ValueError:
#             #session.reset()
#             return view.base(view.member_setting_avatar(
#                         user, mid_src='',
#                         message='文件太大了，我吃不消哇~'), user, siteName)

# class member_avatar_crop:
#     @session.login_required
#     def POST(self):
#         crop_data = web.input()
#         path = crop_data['path']
#         x = crop_data['x']
#         y = crop_data['y']
#         w = crop_data['w']
#         h = crop_data['h']
#         s = utils.make_thumb_crop(path, x, y, w, h)
#         session.reset()
#         raise web.seeother('/settings')

#         # return view.base(view.member_setting_avatar(
#         #                 user, mid_src='',
#         #                 message='头像更新成功~'), user, siteName)
#         #return view.test(path, x, y, w, h, s)



#邮箱提醒开启/关闭
class email_subscribe:
    @session.login_required
    def POST(self):
        action = web.input().subscribe
        users.email_subscribe(user.id, action)
        s = 's'
        return s




