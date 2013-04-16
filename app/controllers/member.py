#!/usr/bin/env python
# coding: utf-8

import web
import time
import datetime

from config import view, site_name
from app.helpers import session
from app.models import users, postModel, nodeModel, notification

siteName = site_name
user = session.get_session()


class member_home:
    def GET(self, username, p=1):
        u = users.get_user_by_username(username)
        print user

        if u:
            page = int(p)
            perpage = 5
            offset = (page - 1) * perpage

            created_posts = postModel.getCreatedPostsByUserId(u.id, offset, perpage).list()

            nodes = []
            for i in xrange(len(created_posts)):
                nodes += nodeModel.getNodesByNodeId(created_posts[i].nodeId)

            #得到资料
            profile = users.get_profile_by_user_id(u.id)

            #是否登录，
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
                is_voted = None
                notification_results = None
                notification_num = None
                ntf_list = None
                ntf_posts = None
                ntf_users = None
                
            return view.base(view.member_home(u, profile, created_posts, nodes, user), user, siteName, rights, ntf_list, notification_num, ntf_posts, ntf_users)
        else:
            raise web.notfound()

class member_home_post_load_more:
    def GET(self, username, page_num):
        u = users.get_user_by_username(username)
        page = int(page_num)
        perpage = 5
        offset = (page - 1) * perpage

        # url = web.ctx.get('path')
        # if int(url.count('recent')) == 0:
        created_posts = postModel.getCreatedPostsByUserId(u.id, offset, perpage).list()

        nodes = []
        for i in xrange(len(created_posts)):
            nodes += nodeModel.getNodesByNodeId(created_posts[i].nodeId)

        return view.post_list_member_profile_more(u, created_posts, nodes)
        
#喜欢的片段
class member_likes:
    def GET(self,username, p=1):
        u = users.get_user_by_username(username)
        if u:
            page = int(p)
            perpage = 5
            offset = (page - 1) * perpage

            liked_pids = postModel.getLikedPostsByUserId(u.id, offset, perpage).list()

            liked_posts = []
            for i in xrange(len(liked_pids)):
                liked_posts += postModel.getPostsByPostId(liked_pids[i].pid)

            authors = []
            for i in xrange(len(liked_posts)):
                authors += users.get_users_by_id(liked_posts[i].postAuthor)

            nodes = []
            for i in xrange(len(liked_posts)):
                nodes += nodeModel.getNodesByNodeId(liked_posts[i].nodeId)

            #得到资料
            profile = users.get_profile_by_user_id(u.id)

            #是否登录，
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
                is_voted = None
                notification_results = None
                notification_num = None
                ntf_list = None
                ntf_posts = None
                ntf_users = None
            return view.base(view.member_favorite(u, profile, liked_posts, nodes, authors, user), user, siteName, rights, ntf_list, notification_num, ntf_posts, ntf_users)
        else:
            raise web.notfound()

class member_home_post_like_more:
    def GET(self, username, page_num):
        u = users.get_user_by_username(username)
        page = int(page_num)
        perpage = 5
        offset = (page - 1) * perpage

        liked_pids = postModel.getLikedPostsByUserId(u.id, offset, perpage).list()

        liked_posts = []
        for i in xrange(len(liked_pids)):
            liked_posts += postModel.getPostsByPostId(liked_pids[i].pid)

        authors = []
        for i in xrange(len(liked_posts)):
            authors += users.get_users_by_id(liked_posts[i].postAuthor)

        nodes = []
        for i in xrange(len(liked_posts)):
            nodes += nodeModel.getNodesByNodeId(liked_posts[i].nodeId)

        return view.post_list_member_like_more(u, liked_posts, nodes, authors)

#创建的话题
class member_node:
    def GET(self, username, p=1):
        u = users.get_user_by_username(username)
        profile = users.get_profile_by_user_id(u.id)

        page = int(p)
        perpage = 10
        offset = (page - 1) * perpage

        nodeList = nodeModel.getCreatedNodesByUserId(u.id, offset, perpage).list()

        #是否登录，
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
            is_voted = None
            notification_results = None
            notification_num = None
            ntf_list = None
            ntf_posts = None
            ntf_users = None

        return view.base(view.member_node(u, profile, nodeList, user),user, siteName, rights, ntf_list, notification_num, ntf_posts, ntf_users)

class member_home_node_load_more:
    def GET(self, username, page_num):
        u = users.get_user_by_username(username)
        page = int(page_num)
        perpage = 10
        offset = (page - 1) * perpage

        nodeList = nodeModel.getCreatedNodesByUserId(u.id, offset, perpage).list()

        return view.node_list_member_profile_more(u, nodeList)

#参与的话题
class contributed_node:
    def GET(self, username, p=1):
        u = users.get_user_by_username(username)
        profile = users.get_profile_by_user_id(u.id)

        page = int(p)
        perpage = 10
        offset = (page - 1) * perpage

        posts = postModel.groupGetCreatedPostsByUserId(u.id, offset, perpage).list()
        nodeids = []
        for i in xrange(len(posts)):
            nodeids += str(posts[i].nodeId).split()

        nodeList = []
        for i in xrange(len(nodeids)):
            nodeList += nodeModel.getNodesByNodeId(nodeids[i])

        authors = []
        for i in xrange(len(nodeList)):
            authors += users.get_users_by_id(nodeList[i].node_author)

        #是否登录，
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
            is_voted = None
            notification_results = None
            notification_num = None
            ntf_list = None
            ntf_posts = None
            ntf_users = None

        return view.base(view.member_node_contributed(u, profile, nodeList, authors, user),user, siteName, rights, ntf_list, notification_num, ntf_posts, ntf_users)

class contributed_node_more:
    def GET(self, username, page_num):
        u = users.get_user_by_username(username)
        page = int(page_num)
        perpage = 10
        offset = (page - 1) * perpage

        posts = postModel.groupGetCreatedPostsByUserId(u.id, offset, perpage).list()
        nodeids = []
        for i in xrange(len(posts)):
            nodeids += str(posts[i].nodeId).split()

        nodeList = []
        for i in xrange(len(nodeids)):
            nodeList += nodeModel.getNodesByNodeId(nodeids[i])

        authors = []
        for i in xrange(len(nodeList)):
            authors += users.get_users_by_id(nodeList[i].node_author)

        return view.node_list_contributed_more(nodeList, authors)
    