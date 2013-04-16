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

class index:
    def GET(self):
        return '{"users":[{"name":"<b>aluu</b>","avatar":"http://img3.douban.com/icon/u1154663-312.jpg","username":"<b>aluu</b>"}]}'
        # return {"users":[{"username":"J.叔","avatar":"http://img3.douban.com/icon/u2042162-419.jpg","uid":"<b>po</b>et229","id":"poet229"},{"username":"一见你就笑","avatar":"http://img3.douban.com/icon/u43088802-34.jpg","uid":"<b>po</b>st-punker","id":"post-punker"},{"username":"<b>po</b>werblue","avatar":"http://img3.douban.com/icon/u1295540-1.jpg","uid":"monkey1985","id":"monkey1985"},{"username":"ping<b>po</b>ngA","avatar":"http://img3.douban.com/icon/u1260832-221.jpg","uid":"cherryjue","id":"cherryjue"},{"username":"Hooo<b>po</b>","avatar":"http://img3.douban.com/icon/u2061460-27.jpg","uid":"Hoooo<b>po</b>","id":"Hoooopo"}]}