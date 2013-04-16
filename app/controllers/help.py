#!/usr/bin/env python
# coding: utf-8

import datetime
import web

from app.models import help
from app.helpers import session, email_templates
from config import view, site_name

user = session.get_session()
siteName = site_name

class feedback:
    def GET(self):
        # try:
        return view.base02(view.feedback(user), user, siteName)
        # except Exception, e:
        #     raise web.internalerror()

    def POST(self):
        content = web.input().content
        if content:
            douban_id = user.douban_id
            help.save_feedback(content, douban_id)
            email_templates.send_feedback(user, content)
            return '{"info":"提交成功，感谢你的反馈 :)","status":"y"}'

