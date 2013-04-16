#!/usr/bin/env python
# coding: utf-8

import web
from config import view, site_name, site_domain
from app.helpers import session
from app.models import users

user = session.get_session()
siteName = site_name

ntf_list = None
notification_num = None
ntf_posts = None
ntf_users = None

class update:
    def GET(self):
        if user.is_logged:
            per = users.get_permission_by_douid(user.douban_id)
            rights = per[0].rights
            if rights > 1:
                return view.base(view.update(), user, siteName, rights, ntf_list, notification_num, ntf_posts, ntf_users)
            else:
                raise web.notfound()
        else:
            raise web.notfound()

class about:
    def GET(self):
        if user.is_logged:
            per = users.get_permission_by_douid(user.douban_id)
            rights = per[0].rights
        else:
            rights = 0
        return view.base(view.about(), user, siteName, rights, ntf_list, notification_num, ntf_posts, ntf_users)

class policy:
    def GET(self):
        if user.is_logged:
            per = users.get_permission_by_douid(user.douban_id)
            rights = per[0].rights
        else:
            rights = 0
        return view.base(view.policy(), user, siteName, rights, ntf_list, notification_num, ntf_posts, ntf_users)

class guideline:
    def GET(self):
        if user.is_logged:
            per = users.get_permission_by_douid(user.douban_id)
            rights = per[0].rights
        else:
            rights = 0
        return view.base(view.guideline(), user, siteName, rights, ntf_list, notification_num, ntf_posts, ntf_users)

class privacy:
    def GET(self):
        if user.is_logged:
            per = users.get_permission_by_douid(user.douban_id)
            rights = per[0].rights
        else:
            rights = 0
        return view.base(view.privacy(), user, siteName, rights, ntf_list, notification_num, ntf_posts, ntf_users)

class blog:
    def GET(self):
        if user.is_logged:
            per = users.get_permission_by_douid(user.douban_id)
            rights = per[0].rights
        else:
            rights = 0
        return view.base(view.blog(), user, siteName, rights, ntf_list, notification_num, ntf_posts, ntf_users)