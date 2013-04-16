#!/usr/bin/env python
# coding: utf-8

import random
import re
import md5
import time
import datetime
import hashlib
import web
from web import form

from app.models import users
from app.helpers import session
from app.helpers import email_templates

from config import view, encryption_key, site_name, db

user = session.get_session()
siteName = site_name
vemail = form.regexp(r'.+@.+', '邮箱格式不对')
p = re.compile(r"(?:^|\s)[-a-z0-9_.+]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)", re.IGNORECASE)

#表单
login_form = form.Form(
    form.Textbox('email', 
        form.notnull, vemail,
        description='邮箱:'),
    form.Password('password', 
        form.notnull,
        description='密码:'),
    validators = [
        form.Validator('邮箱地址或密码不正确', 
            lambda i: users.is_correct_password(i.email, i.password))
    ]
)

register_form = form.Form(
    form.Textbox('username', 
        form.notnull,
        form.Validator('用户名已存在.',
        lambda x: users.is_username_available(x)),
        #form.Validator('请以字母开头，不超过15个字母、数字，保存后不可修改', #todo
        #lambda x: users.is_username_available(x)),
        description='用户名(以字母开头的2-16个字母、数字组合):'),

    form.Textbox('email', 
        form.notnull, vemail,
        form.Validator('邮箱已经存在.', 
        lambda x: users.is_email_available(x)),
        description='邮箱:'),

    form.Password('password', 
        form.notnull,
        form.Validator('密码不能少于6个字符.', 
        lambda x: users.is_valid_password(x)),
        description='密码:'),
    form.Textbox('nickname', 
        form.notnull,
        description='昵称:'),
)

forgot_password_form = form.Form(
    form.Textbox('email', 
        form.notnull,
        # form.Validator('请检查您的邮箱地址', 
        # lambda x: not users.is_email_available(x)),
        description='你的邮箱地址:'),
    # validators = [
    #     form.Validator('邮箱地址不存在', 
    #         lambda x: users.is_email_exist(x))
    # ]        
)

reset_password_form = form.Form(
     form.Password('password', 
        form.notnull,
        form.Validator('密码不能少于6个字符.', 
        lambda x: users.is_valid_password(x)),
        description='密码:'),
     form.Password('again', 
        form.notnull,
        form.Validator('密码不能少于6个字符.', 
        lambda x: users.is_valid_password(x)),
        description='再输一次密码:'),
)

#模板调用
def render_account(show='all', 
    login_form=login_form(), register_form=register_form(), forgot_password_form=forgot_password_form(), reset_password_form=reset_password_form(), token = '',
    on_success_message='', error_message=''):
    rights=None
    ntf_list=None
    notification_num=None
    ntf_posts=None
    ntf_users=None
    return view.base(
        view.account(show, login_form, register_form, forgot_password_form, reset_password_form, token, on_success_message, error_message), user, site_name, rights, ntf_list, notification_num, ntf_posts, ntf_users
        )

# class index:
#     def GET(self):
#         return render_account(show='all')

#登录
class login:
    def GET(self):

        rights=None
        ntf_list=None
        notification_num=None
        ntf_posts=None
        ntf_users=None

        return view.base(view.home(), user, site_name, rights, ntf_list, notification_num, ntf_posts, ntf_users
        )

        # return render_account(show='login_only')

        # raise web.seeother('/')
    
    def POST(self):
        f = self.form()
        if not f.validates(web.input(_unicode=False)):
            show = web.input(show='all').show
            return render_account(show, login_form=f)
        else:
            session.login(f.d.email)
            # raise web.seeother('/')
            raise web.seeother(session.get_last_visited_url())
    
    def form(self):
        return login_form()

#注册    
class register:
    def GET(self):
        # raise web.seeother('/')
        # NOTE: 以后改回来
        return render_account(show='register_only')
    
    def POST(self):
        f = self.form()
        if not f.validates(web.input(_unicode=False)):
            show = web.input(show='all').show
            return render_account(show, register_form=f)
        elif len(f.d.username) > 16 :
            return render_account(
                show = 'register_only',
                error_message = '<span class="alert alert-error">不能超过16位</span>',
                register_form=f
            )
        elif len(f.d.username) < 2 :
            return render_account(
                show = 'register_only',
                error_message = '<span class="alert alert-error">不能少过2位</span>',
                register_form=f
            )
        elif not (re.search('^[a-zA-Z]{1}[\w\-]{5,15}$', f.d.username)):
            return render_account(
                show = 'register_only',
                error_message = '<span class="alert alert-error">请以字母开头，6-16个字母、数字</span>',
                register_form=f
            )
        else:
            users.create_account(f.d.username, f.d.email, f.d.password, f.d.nickname)
            session.login(f.d.email)
            raise web.seeother('/')
    
    def form(self):
        return register_form()

#忘记密码
class forgot:
    def GET(self):
        return render_account(show='forgot_password_only')
    
    def POST(self):
        f = self.form()
        show = web.input(show='all').show
        timestamp = time.mktime(time.localtime())#时间戳
        
        if not f.validates(web.input(_unicode=False)):
            return render_account(show, forgot_password_form=f)

        prev_timestamp = users.get_last_timestamp(f.d.email)
        g = timestamp - prev_timestamp
        
        if not (p.search(f.d.email)):
            return render_account(
                show='forgot_password_only',
                error_message='<span class="alert alert-error">你输入的电子邮件地址不符合规则</span>'
            )

        elif not users.is_email_exist(f.d.email):
            return render_account(
                show='forgot_password_only',
                error_message='<span class="alert alert-error">邮箱地址不存在</span>'
            )
        elif g < 3600:
            return render_account(
                show='forgot_password_only',
                error_message='<span class="alert alert-error">次数太频繁我会受不了，请1小时之后再来。</span>'
            )
        
        else:
            all = list('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSQUVWXYZ')
            token = ''
            for i in range(32):
                index = random.randint(0,len(all)-1)
                token = token + all[index] #生成32位随机数 -> token
            #token = ''.join([str(random.randint(0, 9)) for i in range(32)])
            tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp)) #格式化时间戳
            users.passwordForgot(f.d.email, token, timestamp) #传递email到model,将取密码的记录存到库中
            user = users.get_user_by_email(f.d.email)
            ua = web.ctx.env.get('HTTP_USER_AGENT')
            ip = web.ctx.ip
            email_templates.forgot(user, token, ua, ip, tm)
            return render_account(
                show='reset_password_success', 
                on_success_message='邮件已发送，请查收您的邮箱.'
            )
    
    def form(self):
        return forgot_password_form()

#重置密码
class reset:
    def GET(self, token):
        newTime = time.mktime(time.localtime())#得到访问reset页面的时间
        #s_newTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(newTime))
        timestamp = users.get_timestamp(token)#将 token 传到 model ,寻找对应的timestamp
        #s_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        noExist = users.passwordReset(token)#将 token 传到 model 中进行比对，看是否正确
        if noExist :
            return view.base(
                view.token_not_found(error_message = '<span class="alert alert-error">sorry，token不存在，你访问的地址无效，请检查你的url是否写错。</span>'),
                user, site_name
            )
        elif newTime - timestamp > 604800 :
            #users.delete_SesetLog(token)#删除此过期的记录
            return view.base(
                view.token_not_found(error_message = '<span class="alert alert-error">时间过去一周多，地址已经失效了。</span>'),
                user, site_name
            )
        elif users.get_valid(token) == 1:
            return view.base(
                view.token_not_found(error_message = '<span class="alert alert-error">地址已经失效了。</span>'),
                user, site_name
            )
        else:
            return render_account(
                show = 'reset_password_only',
                token = token
            )

    def POST(self, token):
        f = self.form()
        show = web.input().show
        if not f.validates(web.input(_unicode=False)):
            return render_account(show='reset_password_only', reset_password_form=f, token = token)
        elif f.d.password != f.d.again:
            return render_account(
                show = 'reset_password_only',
                token = token,
                error_message = '<span class="alert alert-error">两次输入的密码不一致</span>'
            )
        else:
            id = users.get_user_by_email(users.get_email(token)).get('id',False)
            users.update(id, password=hashlib.md5(f.d.password + encryption_key).hexdigest()) #更新密码 todo:是不是应该写到model里的
            users.update_valid(token) #更改 valid 为 1 表示已经更改了密码
            return render_account(
                show = 'reset_password_success',
                on_success_message = '密码已更新'
            ) 

    def form(self):
        return reset_password_form()

#退出
class logout:
    def GET(self):
        session.logout()
        # siteName = site_name
        #raise web.seeother(web.ctx.environ['HTTP_REFERER'])
        raise web.seeother('/account/bye')
        # return view.base01(view.landing(), siteName)
    
class goodbye:
    def GET(self):
        return view.base01(view.goodbye(), site_name)

#着陆页ajax验证用户名是否可用
class check_username:
    def POST(self):
        data = web.input()
        username = data.param
        if users.is_username_available(username):
            return "y"
        else:
            return "这个用户名太受欢迎已被注册了"

#着陆页ajax验证邮箱是否可用
class check_email:
    def POST(self):
        data = web.input()
        email = data.param
        if users.is_email_available(email):
            return "y"
        else:
            return "这个邮箱已经被使用了"

#着陆页ajax登录
class landing_login:
    def POST(self):
        data = web.input()
        email = data.loginEmail
        password = data.loginPassword
        if not users.is_correct_password(email, password):
            # Validform插件需要返回JSON格式的数据
            return '{"info":"邮箱或密码有误","status":"n"}' 
        else:
            session.login(email)
            # raise web.seeother('/')
            return '{"info":"登录成功，欢迎回来","status":"y"}'

#验证注册邮箱
class confirm_email:
    @session.login_required
    def GET(self, token):
        CE = users.get_confirm_email(token)
        if CE :
            new = time.time() #得到访问当前页面时的时间
            old = time.mktime(CE.get('timestamp').timetuple())
            if new - old > 86400: #24小时
                return view.base(view.confirm_email(msg="out-time"), user, site_name)
            else:
                users.update_confirm_email(token)
                return view.base(view.confirm_email(msg="succes"), user, site_name)
        else:
            raise web.notfound()

#着陆页找回密码
class landing_forgot:
    def POST(self):
        data = web.input()
        email = data.forgotEmail
        timestamp = time.mktime(time.localtime())
        prev_timestamp = users.get_last_timestamp(email)
        g = timestamp - prev_timestamp

        if users.is_email_available(email):
            return '{"info":"此邮箱尚未注册过","status":"n"}'
        elif g < 3600:
            return '{"info":"太频繁了","status":"n"}'
        else:
            all = list('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSQUVWXYZ')
            token = ''
            for i in range(32):
                index = random.randint(0,len(all)-1)
                token = token + all[index] #生成32位随机数 -> token
            #token = ''.join([str(random.randint(0, 9)) for i in range(32)])
            tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp)) #格式化时间戳
            users.passwordForgot(email, token, timestamp) #传递email到model,将取密码的记录存到库中
            user = users.get_user_by_email(email)
            ua = web.ctx.env.get('HTTP_USER_AGENT')
            ip = web.ctx.ip
            email_templates.forgot(user, token, ua, ip, tm)
            return '{"info":"找回密码邮件已发送，请检查邮箱","status":"y"}'

#申请开通权限
class apply_for_permission:
    @session.login_required
    def POST(self):
        data = web.input()
        douban_id = data.douban_id
        email = data.email
        reason = data.reason
        users.save_user_apply_permission_log(douban_id, email, reason)

        #发送邮件
        apply_time = datetime.datetime.now()
        apply_user = users.get_douban_user_by_doubanid(douban_id)
        #发送通知邮件 给管理员们
        email_templates.apply_for_permission(apply_user, apply_time, email)

        return '{"info":"申请已发送，谢谢你的支持。","status":"y"}'

