#!/usr/bin/env python
# coding: utf-8

import web
import datetime
from config import view
from app.helpers import session, paging, misc, email_templates
from app.models import users, admin, postModel, nodeModel, help

user = session.get_session()

#后台管理首页
class home:
    @session.login_required
    def GET(self):
        per = users.get_permission_by_douid(user.douban_id)
        rights = per[0].rights
        if rights > 1 : #管理员权限
            #post
            rec_posts = admin.get_rec_posts()
            rec_nodes = admin.get_rec_nodes()

            #post
            postList = []
            for i in xrange(len(rec_posts)):
                postList += postModel.getPostsByPostId(rec_posts[i].pid)

            a = []
            for post in postList:
                a += str(post.postAuthor).split()

            post_authors = []
            for i in xrange(len(a)):
                post_authors += users.get_users_by_id(a[i])

            p= []
            for post in postList:
                p += str(post.nodeId).split()

            post_nodes = []
            for i in xrange(len(p)):
                post_nodes += nodeModel.getNodesByNodeId(p[i])

            #node
            nodeList = []
            for i in xrange(len(rec_nodes)):
                nodeList += nodeModel.getNodesByNodeId(rec_nodes[i].nid)

            n = []
            for node in nodeList:
                n += str(node.node_author).split()

            node_authors = []
            for i in xrange(len(n)):
                node_authors += users.get_users_by_id(n[i])
            
            # if rec_nodes or rec_posts:
            return view.template_admin(view.admin_home(postList, post_authors, post_nodes,  nodeList, node_authors))
        else:
            raise web.notfound()

#推荐话题到首页
class rec_node:
    @session.login_required
    def POST(self):
        per = users.get_permission_by_douid(user.douban_id)
        rights = per[0].rights
        if rights > 1: #权限判断
            nid = web.input().nid
            admin.admin_rec_home_post(nid=nid)
            s = 's'
            return s

#推荐片段到首页
class rec_post:
    @session.login_required
    def POST(self):
        per = users.get_permission_by_douid(user.douban_id)
        rights = per[0].rights
        if rights > 1: #权限判断
            pid = web.input().pid
            admin.admin_rec_home_post(pid=pid)
            s = 's'
            return s 

#保存推荐片段排序
class save_sort:
    @session.login_required
    def POST(self):
        per = users.get_permission_by_douid(user.douban_id)
        rights = per[0].rights
        if rights > 1:
            data = web.input()
            pids = data.pids.split(',')
            nids = data.nids.split(',')
            admin.save_sort(pids, nids)
            s = 's'
            return s

#删除推荐片段
class del_rec_post(object):
    @session.login_required
    def POST(self):
        per = users.get_permission_by_douid(user.douban_id)
        rights = per[0].rights
        if rights > 1:
            pid = web.input().pid
            admin.del_rec_post(pid)
            # s = 's'
            # return s

#删除推荐话题
class del_rec_node(object):
    @session.login_required
    def POST(self):
        per = users.get_permission_by_douid(user.douban_id)
        rights = per[0].rights
        if rights > 1:
            nid = web.input().nid
            admin.del_rec_node(nid)
            # return nid

#用户管理
class admin_users():
    @session.login_required
    def GET(self):
        #得到当前用户的权限
        per = users.get_permission_by_douid(user.douban_id)
        rights = per[0].rights
        if rights > 1:
            results_per_page = 8 #每页显示8个用户
            default_order = 'id'

            i = web.input(start=0, order=default_order, desc='desc', query='')
            start = int(i.start)
            # context = context or 'all'
            # user_id = session.is_logged() and session.get_user_id()

            results, num_results = admin.query(query=i.query, 
                offset=start, limit=results_per_page, order=i.order + ' ' + i.desc, user_id=None)

            pager = web.storage(paging.get_paging(start, num_results, 
                results_per_page=results_per_page, window_size=1))

            u = user

            #查询用户权限表
            douban_id_list = []
            users_list = list(results)
            for i in xrange(len(users_list)):
                douban_id_list += users_list[i].douban_id.split()

            permissions = []
            for i in xrange(len(douban_id_list)):
                permissions += users.get_permission_by_douid(douban_id_list[i])

            admin_list = []
            for i in xrange(len(permissions)):
                if permissions[i].operator:
                    admin_list += users.get_users_by_id(permissions[i].operator)
                else:
                    admin_list += "s"

            timestrf = misc.timestrf

            return view.template_admin(view.admin_users(users_list, pager, u, permissions, rights, timestrf, admin_list))
        else:
            raise web.notfound()

#修改用户权限
class change_user_rights():
    @session.login_required
    def POST(self):
        per = users.get_permission_by_douid(user.douban_id)
        rights = per[0].rights
        if rights > 1:
            data = web.input()
            douban_id = data.douban_id
            rights = data.rights
            operator = user.id
            operating_ts = datetime.datetime.now()
            users.change_user_permission(douban_id, rights, operator, operating_ts)


#删除用户
class del_users():
    @session.login_required
    def POST(self):
        per = users.get_permission_by_douid(user.douban_id)
        rights = per[0].rights
        if rights > 1:
            data = web.input()
            uid = data.uid
            #note : 只是设为了close 1 没有删除，未做完
            users.update(uid, close = 1)
        

#权限申请管理
class apply_for_permission:
    @session.login_required
    def GET(self, result=''):
        per = users.get_permission_by_douid(user.douban_id)
        rights = per[0].rights

        if rights > 1:
            results_per_page = 8 #每页显示8条记录
            default_order = 'id'

            i = web.input(start=0, order=default_order, desc='desc', query='', result='')
            start = int(i.start)
            result = i.result

            results, num_results = users.get_applys(query=i.query, 
                offset=start, limit=results_per_page, order=i.order + ' ' + i.desc, user_id=None, result=result)

            pager = web.storage(paging.get_paging(start, num_results, 
                results_per_page=results_per_page, window_size=1))

            apply_list = list(results)

            admin_list = []
            for i in xrange(len(apply_list)):
                admin_list += users.get_users_by_id(apply_list[i].operator)

            user_list = []
            for i in xrange(len(apply_list)):
                user_list += users.get_douban_users_by_doubanid(apply_list[i].douban_id)

            return view.template_admin(view.admin_apply_for_permission(apply_list, pager, admin_list, user_list, result))
        else:
            raise web.notfound

#管理员处理权限申请
class apply_operate:
    @session.login_required
    def POST(self):
        per = users.get_permission_by_douid(user.douban_id)
        rights = per[0].rights
        if rights > 1:
            data = web.input()
            id = data.apply_id #申请记录的id
            douban_id = data.douban_id  #申请用户的豆瓣id
            apply_email = data.apply_email #申请时留的邮箱
            apply_result = int(data.apply_result) #申请结果 1 通过 0 未通过

            operator = user.id
            operating_ts = datetime.datetime.now()
            rights = apply_result

            #修改Log管理操作信息
            users.update_user_apply_permission_log(id, operator, operating_ts, apply_result)

            
            apply_user = users.get_douban_user_by_doubanid(douban_id)
            if apply_result == -1: #忽略申请 鉴于可能有乱填邮件地址的情况 note 其实可以去掉这个判断
                pass
            elif apply_result == 1: #申请通过
                #修改用户权限
                users.change_user_permission(douban_id, rights, operator, operating_ts)
                #发送通知邮件
                email_templates.email_to_user_for_apply_success(apply_user, apply_email)
                #
            elif apply_result == 0: #申请未通过
                #修改用户权限
                users.change_user_permission(douban_id, rights, operator, operating_ts)
                #发送通知邮件
                email_templates.email_to_user_for_apply_fail(apply_user, apply_email)

            mes = '处理完毕'
            return mes
        else:
            raise web.notfound

class feedback:
    @session.login_required
    def GET(self, result=''):
        per = users.get_permission_by_douid(user.douban_id)
        rights = per[0].rights
        if rights > 1:
            results_per_page = 10
            default_order = 'id'

            i = web.input(start=0, order=default_order, desc='desc', query='')
            start = int(i.start)

            results, num_results = help.query(query=i.query, 
                offset=start, limit=results_per_page, order=i.order + ' ' + i.desc)

            pager = web.storage(paging.get_paging(start, num_results, 
                results_per_page=results_per_page, window_size=1))

            results = list(results)
            user_list = []
            for i in xrange(len(results)):
                if users.get_douban_users_by_doubanid(results[i].douban_id):
                    user_list += users.get_douban_users_by_doubanid(results[i].douban_id)
                else:
                    user_list += []

            return view.template_admin(view.admin_feedback(results, user_list, pager))

# 查看邮箱激活记录
class confirm_log:
    @session.login_required
    def GET(self, c=''):
        per = users.get_permission_by_douid(user.douban_id)
        rights = per[0].rights
        if rights > 2:
            results_per_page = 10
            default_order = 'id'

            i = web.input(start=0, order=default_order, desc='desc', query='', c ='')
            start = int(i.start)
            c = i.c

            results, num_results = admin.confirm_log_query(query=i.query, 
                offset=start, limit=results_per_page, order=i.order + ' ' + i.desc, c=c)

            pager = web.storage(paging.get_paging(start, num_results, 
                results_per_page=results_per_page, window_size=1))

            results = list(results)

            if c == '1' or c == '':
                user_list = []
                for i in xrange(len(results)):
                    user_list += users.get_douban_users_by_doubanid(results[i].douban_id)
            elif c == '0':
                user_list = []

            return view.template_admin(view.admin_confirm(results, user_list, pager, c))
