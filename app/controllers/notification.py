#!/usr/bin/env python
# coding: utf-8

import web
from config import view, site_name
from app.helpers import session
from app.models import notification

siteName = site_name
user = session.get_session()

#设为已读
class make_single_read:
    def POST(self):
        id = web.input().id
        notification.make_single_read(id, user.id)
        return '{"status": "y", "info": "更新成功"}'

class make_all_read:
    def POST(self):
        id_list = web.input().id_list.split(',')
        notification.make_all_read(id_list, user.id)
        s = 's'
        return s
        