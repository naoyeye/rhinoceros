#!/usr/bin/env python
# coding: utf-8

# import random
# import re
import md5
import time
import datetime
import web

from app.models import users
from app.helpers import session
from app.helpers import email_templates

from config import view, site_name, db

user = session.get_session()
siteName = site_name

#欢迎页面设置 个人资料 邮箱
class welcome:
    def GET(self, arg):

        if user.username == arg:
            #如果是重新填写邮箱
            if web.input().has_key('action'):
                if web.input().action == 'e':
                    #删除之前的激活记录
                    users.del_verification_data_by_douban_id(user.douban_id)
                    return view.base02(view.welcome_set_email(user), user, siteName)
                else:
                    raise web.notfound()
            else:
                return view.base02(view.welcome_set_email(user), user, siteName)
        else:
            raise web.notfound()

    def POST(self, arg):
        try:
            if user.username == arg:
                email = web.input().regEmail
                #发送验证邮件
                token = md5.md5(time.ctime() + email).hexdigest()
                #判断邮箱激活表中是否有此email或者douban_id
                if not users.user_exist_in_table_confirm_email(email, user.douban_id):
                    try:
                        email_templates.msg_new_user_email(user, email, token)
                        #保存记录到数据库
                        users.save_confirm_email(email, user.douban_id, token)
                        #跳转到邮件发送成功页面
                        return web.seeother('/welcome/'+ user.username +'/send_email_feedback?status=succesful')
                    except Exception, e:
                        print 'error--------'
                        print e
                        return web.seeother('/welcome/'+ user.username +'/send_email_feedback?status=failed')
                else:
                    #数据库中已经有记录了
                    return web.seeother('/welcome/'+ user.username +'/send_email_feedback?status=duplicate')
            else:
                raise web.notfound()
        except Exception, e:
            # raise web.notfound()
            print e
            return web.seeother('/welcome/'+ user.username +'/send_email_feedback?status=failed')

        # #如果数据库中没有此用户的豆瓣id，则创建
        # if users.is_douban_id_available(user.douban_id):
        #     #创建用户
        #     users.create_douban_account(
        #         douban_id = douban_id,
        #         username = user.username,
        #         nickname = user.nickname,
        #         email=email,
        #         avatarPath = user.avatarPath,
        #         ipAddress = web.ctx.ip,
        #         lastLoginIP = web.ctx.ip,
        #         nicknameChangeTime = datetime.datetime.now(),
        #         via = 1,
        #         lastLoginTime = datetime.datetime.now()
        #     )

        #     #得到刚刚插入的用户id
        #     last_user_id = db.query("SELECT LAST_INSERT_ID()");

        #     #新建用户资料
        #     users.insert_profile(last_user_id, city = user.city, bio = user.desc )

        #     #如果权限表中没有此用户，增加，并把权限设为 0
        #     if not users.is_user_exist_in__permission(douban_id):
        #         db.insert('_permission', douban_id = douban_id, rights = 0)

        # #如果是已注册的旧用户，则更新用户信息。- 用户可能换了昵称或者头像
        # else:
        #     users.update_user_by_douid(
        #         douban_id,
        #         email=email,
        #         nickname = user.nickname,
        #         nicknameChangeTime = datetime.datetime.now(),
        #         avatarPath = user.avatarPath,
        #         lastLoginIP = web.ctx.ip,
        #         lastLoginTime = datetime.datetime.now()
        #     )

        #     #得到刚刚插入的用户id
        #     last_user_id = db.query("SELECT LAST_INSERT_ID()");

        #     #判断资料表中是否已经存在此用户：
        #     if users.is_user_profile_changed(last_user_id):
        #         #更新用户资料
        #         users.update_profile(last_user_id, city = user.city, bio = user.desc )
        #     else:
        #         #新建用户资料
        #         users.insert_profile(last_user_id,
        #             city = user.city,
        #             bio = user.desc
        #         )

        # #清空session，为下一次装填做准备，以免占用太多空间 - Maybe？ #note
        # session.clear_douban_callback()

        # #session 中保存用户信息 设为登录
        # session.douban_login(douban_id)

        # print '========================'
        # print user.items()
        # print '========================'
        
        # #设置完资料后，跳转到之前浏览器的页面
        # raise web.seeother(session.get_last_visited_url())

class send_email_feedback:
    def GET(self, arg):
        if user.username == arg:
            status = web.input().status
            email = users.get_confirm_email_by_douban_id(user.douban_id).email
            return view.base02(view.welcome_send_email_feedback(user, status, email), user, siteName)
        else:
            raise web.notfound()


#验证注册邮箱
class welcome_confirm_email:
    def GET(self, token):
        CE = users.get_confirm_email_by_token(token)
        if CE :
            new = time.time() #得到访问当前页面时的时间
            old = time.mktime(CE.get('creation_ts').timetuple())
            if new - old > 86400: #如果超过24小时
                #删除记录
                users.del_verification_data_by_token(token)
                return view.base02(view.welcome_confirm_email(user, msg="out-time", ), user, siteName)
            else:
                try:
                    #通过token得到douban_id，保险起见，session中的douban_id可能已失效 ？#note
                    douban_id = CE.douban_id
                    email = CE.email

                    username = user.username
                    nickname = user.nickname
                    avatarPath = user.avatarPath
                    try:
                        city = user.city
                    except Exception, e:
                        city = None

                    try:
                        desc = user.desc
                    except:
                        desc = None

                    #把 confirm 设为 1
                    users.update_confirm_email(token)

                    #如果这个用户已经在user表中存在，则是旧用户
                    if not users.is_douban_id_available(douban_id):
                        
                        #把邮件地址 等 用户信息 更新到 user 表
                        users.update_user_by_douid(
                            douban_id,
                            email = email,
                            nickname = nickname,
                            avatarPath = avatarPath,
                            nicknameChangeTime = datetime.datetime.now(),
                            lastLoginIP = web.ctx.ip,
                            lastLoginTime = datetime.datetime.now()
                        )
                        #得到刚刚操作的用户id
                        # last_user_id = db.query("SELECT LAST_INSERT_ID()")[0].values()[0]
                        last_user_id = users.get_douban_user_by_doubanid(douban_id).id
                        #查询资料表用是否有此用户
                        if users.is_user_profile_exist(last_user_id):
                            users.update_profile(last_user_id, city = city, bio = desc )
                        else:
                            users.insert_profile(last_user_id, city = city, bio = desc )

                        #清空session，为下一次 douban_login 装填做准备，以免占用太多空间 - 可能需要这么做？ #note
                        # session.clear_douban_callback()

                        #session 设为登录
                        # session.reset()
                        session.douban_login(douban_id)

                    else:
                        #创建用户
                        users.create_douban_account(
                            douban_id = douban_id,
                            username = username,
                            nickname = nickname,
                            email = email,
                            avatarPath = avatarPath,
                            ipAddress = web.ctx.ip,
                            lastLoginIP = web.ctx.ip,
                            nicknameChangeTime = datetime.datetime.now(),
                            lastLoginTime = datetime.datetime.now(),
                            via = 1
                        )

                        #得到刚刚插入的用户id
                        # last_user_id = db.query("SELECT LAST_INSERT_ID()")[0].values()[0]
                        last_user_id = users.get_douban_user_by_doubanid(douban_id).id
                        #新建用户资料
                        users.insert_profile(last_user_id, city = city, bio = desc )

                        #如果权限表中没有此用户，增加，并把权限设为 0
                        if not users.is_user_exist_in__permission(douban_id):
                            db.insert('_permission', douban_id = douban_id, rights = 1)

                        #清空session，为下一次 douban_login 装填做准备，以免占用太多空间 - 可能需要这么做？ #note
                        # session.clear_douban_callback()

                        #session 设为登录
                        session.douban_login(douban_id)

                    return view.base02(view.welcome_confirm_email(user, msg="succes"), user, siteName)
                except Exception, e:
                    # print e
                    # raise web.notfound()
                    return view.test(e)
        else:
            raise web.notfound()
