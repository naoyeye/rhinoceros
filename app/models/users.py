#!/usr/bin/env python
# coding: utf-8

import random
import time
import datetime
import hashlib
import web
import socket
from config import db , encryption_key

#创建帐号
def create_account(username, email, password, nickname):
    #生成10位随机数
    all = list('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSQUVWXYZ')
    randStr = ''
    for i in range(10):
        index = random.randint(0,len(all)-1)
        randStr = randStr + all[index]
    #joinTime = time.mktime(time.localtime())
    currTime = time.strftime('%Y%m%d%H%I%M%S',time.localtime(time.time()))
    #note: 加密：随机数 + 时间 + 邮箱地址 + 密钥. //authKey为找回密码用？ 每个用户都有一个唯一的authKey //现在没用上 囧
    authKey = hashlib.md5(randStr + currTime + email + encryption_key).hexdigest()
    #得到客户端IP地址
    ipAddress = web.ctx.ip

    #昵称时间
    nicknameTime = datetime.datetime.now()

    #入库    
    db.insert('users', username=username, email=email, password=hashlib.md5(password + encryption_key).hexdigest(), nickname=nickname, authKey = authKey, ipAddress = ipAddress, nicknameChangeTime = nicknameTime)#注:password 为混合密钥进行md5加密


#查询邮箱验证 via token
def get_confirm_email(token):
    return web.listget(
        db.select('ConfirmEmail', vars=dict(token=token), 
            where='tokenNum = $token'), 0, {})

#查询邮箱验证 via email
def get_confirm_email_by_email(email):
    return web.listget(
        db.select('ConfirmEmail', vars=dict(email=email), order='id DESC',
            where='email = $email'), 0, {})

# #邮箱已验证
# def update_confirm_email(token):
#     db.update('ConfirmEmail', vars=dict(token=token), where='tokenNum = $token', confirmed=1)

#忘记密码
def passwordForgot(email, token, timestamp):
    #入库
    db.insert('PasswordResetToken', email = email, timestamp = timestamp, token = token , valid = 0)

#重置密码 - 验证token是否正确
def passwordReset(token):
    return not db.select(
        'PasswordResetToken', 
        vars = dict(token=token),
        what = 'count(id) as c', 
        where = 'token = $token')[0].c

#重置密码 - 用token得到旧时间戳
def get_timestamp_by_token(token):
    return web.listget(
        db.select('PasswordResetToken', vars=dict(token=token), 
            where='token = $token'), 0, {})
def get_timestamp(token):
    timestamp = get_timestamp_by_token(token) #用token得到旧时间戳
    return timestamp.get('timestamp', False)
def get_email(token):
    emails = get_timestamp_by_token(token)
    return emails.get('email', False)

#重置密码 - 删除重置密码的记录
# def delete_SesetLog(token):
#     db.delete('PasswordResetToken',
#         vars = dict(token=token),
#         where = 'token = $token')

#重置密码 - 根据email得到上一个email的timestamp
def get_timestamp_by_email(email):
    return web.listget(
        db.select('PasswordResetToken', order='id DESC', vars=dict(email=email), 
            where='email = $email'), 0, {})
def get_last_timestamp(email): 
    timestamp = get_timestamp_by_email(email)
    return timestamp.get('timestamp', False)

#验证 valid 值
def get_valid_by_token(token):
    return web.listget(
        db.select('PasswordResetToken', vars=dict(token=token), 
            where='token = $token'), 0, {})
def get_valid(token): 
    valid = get_valid_by_token(token)
    return valid.get('valid', False)

#更新valid值
def update_valid(token, valid=1):
    db.update('PasswordResetToken', vars=dict(token=token), where='token = $token', valid=1)

def get_user_by_email(email):
    return web.listget(
        db.select('users', vars=dict(email=email), 
            where='email = $email'), 0, {})

def is_email_available(email):
    return not db.select(
        'users', 
        vars = dict(email=email),
        what = 'count(id) as c', 
        where = 'email = $email')[0].c

def is_email_exist(email):
    return db.select(
        'users', 
        vars = dict(email=email),
        what = 'count(id) as c', 
        where = 'email = $email')[0].c

def is_username_available(username):
    return not db.select(
        'users', 
        vars = dict(username=username),
        what = 'count(id) as c', 
        where = 'username = $username')[0].c

def is_valid_password(password):
    return len(password) >= 6

def is_correct_password(email, password):
    user = get_user_by_email(email)
    pwdhash = hashlib.md5(password + encryption_key).hexdigest() #密码混合密钥进行md5加密
    return user.get('password', False) == pwdhash #判断密码是否正确

#更改邮件/密码/昵称
def update(id, **kw):
    db.update('users', vars=dict(id=id), where='id = $id', **kw)

#更改用户资料
#是否需要更改
def is_user_profile_exist(id):
    return db.select(
        'UserProfile', 
        vars = dict(id=id),
        what = 'count(id) as c', 
        where = 'user_id = $id')[0].c

#新增用户资料
def insert_profile(id, **f):
    db.insert('UserProfile', user_id = id, **f)

#更新用户资料
def update_profile(id, **f):
    db.update('UserProfile', vars=dict(id=id), where='user_id = $id', **f)

#读取某用户资料
def get_profile_by_user_id(id):
    return web.listget(
        db.select('UserProfile', vars=dict(id=id), 
            where='user_id = $id'), 0, {})

def get_user_by_id(id):
    return web.listget(
        db.select('users', vars=dict(id=id), 
            where='id = $id'), 0, {})

def get_users_by_id(id):
    return db.select('users', vars=dict(id=id), 
            where='id = $id')

#根据用户名取得昵称等信息
#todo 可以优化/合并的 :p
def get_users_by_username(username):
    return db.select('users', vars=dict(username=username), 
            where = 'username = $username')

def get_user_by_username(username):
    return web.listget(
       db.select('users', vars=dict(username=username), 
            where = 'username = $username'), 0, {})

# def get_nickname(username):
#     u = get_user_by_username(username)
#     return u.get('nickname', False)

# def get_avatar(username):
#     u = get_user_by_username(username)
#     return u.get('avatarPath', False)

# def get_id(username):
#     u = get_user_by_username(username)
#     return u.get('id', False)

# def get_jointime(username):
#     u = get_user_by_username(username)
#     return u.get('joinTime', False)

#得到最新注册的用户 10
def last_users():
    return db.select('users', limit = 18, order='id DESC')

#保存用户头像
def save_user_avatar(user_id, avatar):
    db.update('users', vars=dict(id=user_id), where='id = $id', avatarPath = avatar)


# #根据用户名取得头像
# def get_avatar_by_username(username):
#     return db.select('users', vars=dict(username=username),where='username = $username')

#=====via 豆瓣

#豆瓣用户注册
def create_douban_account(**value):
    db.insert('users', **value)

#更新用户资料
def update_user_by_douid(douban_id, **value):
    db.update('users', vars=dict(douban_id=douban_id), where='douban_id = $douban_id', **value)

#检查豆瓣id在数据库中是否已存在
def  is_douban_id_available(douban_id):
    return not db.select(
        'users', 
        vars = dict(douban_id=douban_id),
        what = 'count(id) as c', 
        where = 'douban_id = $douban_id')[0].c

#通过豆瓣id获得某个用户
def get_douban_user_by_doubanid(douban_id):
    return web.listget(
       db.select('users', vars=dict(douban_id=douban_id), 
            where = 'douban_id = $douban_id'), 0, {})

#通过豆瓣id获得多个用户
def get_douban_users_by_doubanid(douban_id):
    return db.select('users', vars=dict(douban_id=douban_id), 
            where = 'douban_id = $douban_id')

#==== 权限
#查询用户是否已经存在于权限表中
def is_user_exist_in__permission(douban_id):
    return db.select(
        '_permission', 
        vars = dict(douban_id=douban_id),
        what = 'count(id) as c', 
        where = 'douban_id = $douban_id')[0].c

#更改用户权限
def change_user_permission(douban_id, rights, operator, operating_ts):
    db.update('_permission', vars=dict(douban_id=douban_id), where='douban_id = $douban_id', rights = rights, operator = operator, operating_ts = operating_ts)

#得到用户权限
def get_permission_by_douid(douban_id):
    return db.select('_permission', vars=dict(douban_id=douban_id), where='douban_id = $douban_id')

#保存用户申请权限的记录
def save_user_apply_permission_log(douban_id, email, reason):
    db.insert('_apply_permission_log', douban_id = douban_id, email = email, reason = reason)

#更新用户申请权限的记录
def update_user_apply_permission_log(id, operator, operating_ts, apply_result):
    db.update('_apply_permission_log', vars=dict(id=id), where='id = $id', operator = operator, operating_ts = operating_ts, result = apply_result)

#查看某用户是否存在于未处理的权限申请记录表中： 未处理 or 移除/忽略状态
def is_user_exist_in_apply_log(douban_id):
    return db.select(
        '_apply_permission_log', 
        vars = dict(douban_id=douban_id),
        what = 'count(id) as c', 
        where = 'douban_id = $douban_id')[0].c

def get_log_result(douban_id):
    return web.listget(
        db.select(
        '_apply_permission_log', 
        vars = dict(douban_id=douban_id),
        where = 'douban_id = $douban_id'),0, {})

#得到 admin_users 分页
def get_applys(query=None, offset=8, limit=8, order='id desc', user_id=None, result=''):
    table = '_apply_permission_log'

    if result == '-2' or result == '':
        get_where = 'result = -2' #查询未处理的
    elif result == '-1':
        get_where = 'result = -1' #查询移除的
    elif result == '0':
        get_where = 'result = 0' #查询未通过的
    elif result == '1':
        get_where = 'result = 1' #查询已通过的

    results = db.select(table, 
        offset = offset,
        limit = limit,
        order = order,
        where = get_where)

    count = int(db.select(table, what='count(distinct id) as c', where = get_where)[0].c)
    
    return (results, count)
# #更新旧用户的豆瓣id·
# def update_user_doubanid(douban_id, douban_id):
#     db.update('users', vars=dict(douban_id=douban_id), where='douban_id = $douban_id', douban_id = douban_id)

#删除用户
# def del_user(uid):
#     db.delete('users', vars = dict(id=uid), where = 'id = $id')

#==================
#保存邮箱验证
def save_confirm_email(email, douban_id, token):
    db.insert('_confirm_email', email = email, douban_id= douban_id, token = token)

#删除之前的激活邮件记录 #情况： 1. 旧用户 2 重新修改邮件地址
def del_verification_data_by_douban_id(douban_id):
    db.delete('_confirm_email', vars = dict(douban_id=douban_id), where = 'douban_id = $douban_id')

#删除之前的激活邮件记录 #情况：过期
def del_verification_data_by_token(token):
    db.delete('_confirm_email', vars = dict(token=token), where = 'token = $token')

#得到邮箱验证 via douban_id
def get_confirm_email_by_douban_id(douban_id):
    return web.listget(
        db.select('_confirm_email', vars=dict(douban_id=douban_id), 
            where='douban_id = $douban_id'), 0, {})

#得到邮箱验证 via token
def get_confirm_email_by_token(token):
    return web.listget(
        db.select('_confirm_email', vars=dict(token=token), 
            where='token = $token'), 0, {})

#把邮箱标记为已验证
def update_confirm_email(token):
    db.update('_confirm_email', vars=dict(token=token), where='token = $token', confirmed=1)

#Update邮箱
def update_confirm_email_by_douban_id(douban_id, email, token, time):
    db.update('_confirm_email', vars=dict(douban_id=douban_id), where='douban_id = $douban_id', email=email, token=token,  confirmed=0, creation_ts=time)

#查询邮件激活表中是否已经存在此记录
def douban_id_exist_in_table_confirm_email(douban_id):
    return db.select(
        '_confirm_email', 
        vars = dict(douban_id=douban_id),
        what = 'count(id) as c', 
        where = 'douban_id = $douban_id')[0].c

#查询邮箱验证 via douban_id
def user_exist_in_table_confirm_email(email, douban_id):
    return db.select(
        '_confirm_email', 
        vars = dict(email=email, douban_id = douban_id),
        what = 'count(id) as c', 
        where = 'email = $email or douban_id = $douban_id')[0].c

##邮箱提醒开启/关闭
def email_subscribe(user_id, action):
    if action == 'True':
        email_subscribe = 1
    elif action == 'False':
        email_subscribe = 0
    db.update('UserProfile', email_subscribe = email_subscribe, vars = dict(user_id=user_id,),where = 'user_id = $user_id')


