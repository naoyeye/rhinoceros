#!/usr/bin/env python
# coding: utf-8

import web, os
from app.helpers import misc
from app.helpers import utils

#-- openid type config --
OPENID_DOUBAN = 'douban'
OPENID_SINA = 'sina'
OPENID_QQ = 'qq' ##qq weibo

OPENID_TYPE_DICT = {
    OPENID_DOUBAN : "D",
    OPENID_SINA : "S",
    OPENID_QQ : "Q",
}

#-- oauth key & secret config --
APIKEY_DICT = {
    OPENID_DOUBAN : {
        "key" : "xxxx",
        "secret" : "xxxxx",
        "redirect_uri" : "http://www.biubiu.com/connect/douban/callback",
    },
    OPENID_SINA : {
        "key" : "",
        "secret" : "",
        "redirect_uri" : "http://127.0.0.1:5000/connect/sina/callback",
    },
    OPENID_QQ: {
        "key" : "",
        "secret" : "",
        "redirect_uri" : "http://127.0.0.1:5000/connect/qq/callback",
    },
}

# connect to database
# ==============Online Product:==============
#db = web.database(dbn='mysql', db='xxxxx', user='xxxxx', passwd='xxxxx')
# ==============Product Dev:==============
#db = web.database(dbn='mysql', db='xxxxx-dev', user='xxxxx', passwd='xxxxx')
#==============Local Dev:==============
db = web.database(dbn='mysql', db='dbname', user='username', passwd='pwd')

# in development debug error messages and reloader
web.config.debug = True

# in develpment template caching is set to false
cache = False

# global used template functions
globals = utils.get_all_functions(misc)

# the domain where to get the forms from
#site_domain = 'http://0.0.0.0:8080'#本地开发测试用
site_domain = 'xxxx'#你的域名

# the site name where to get the forms from
site_name = 'xxxx'#你的网站名称

# email settings
# mail_sender = 'Biu <help@biubiubiubiu.com>' #请填写你用来发邮件的gmail邮箱
mail_sender = None #请填写你用来发邮件的gmail邮箱

# set global base template
view = web.template.render('app/views', cache=cache,  globals=globals)

# used as a salt
encryption_key = '' #填写随机的字母\数字作为网站密钥

# in production the internal errors are emailed to us
web.config.email_errors = ''
