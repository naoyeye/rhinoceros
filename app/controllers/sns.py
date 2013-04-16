#!/usr/bin/env python
# coding: utf-8

import web
import httplib2
import config
import datetime
import urllib
import collections
from config import view, site_name, db
from app.helpers import session
from app.models import users

siteName = site_name
u = session.get_session()

def httplib2_request(uri, method="GET", body='', headers=None, 
        redirections=httplib2.DEFAULT_MAX_REDIRECTS, 
        connection_type=None, disable_ssl_certificate_validation=True):

    DEFAULT_POST_CONTENT_TYPE = 'application/x-www-form-urlencoded'

    if not isinstance(headers, dict):
        headers = {}

    if method == "POST":
        headers['Content-Type'] = headers.get('Content-Type', 
            DEFAULT_POST_CONTENT_TYPE)

    return httplib2.Http(disable_ssl_certificate_validation=disable_ssl_certificate_validation).\
        request(uri, method=method, body=body,
        headers=headers, redirections=redirections,
        connection_type=connection_type)


class OAuth2Login(object):
    version = '2.0'

    authorize_uri       = ''
    access_token_uri    = ''
    
    def __init__(self, apikey, apikey_secret, redirect_uri, 
            scope=None, state=None, display=None):

        self.apikey = apikey
        self.apikey_secret = apikey_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.state = state
        self.display = display

    def get_login_uri(self):
        qs = {
            'client_id'     : self.apikey,
            'response_type' : 'code',
            'redirect_uri'  : self.redirect_uri,
        }
        if self.display:
            qs['display'] = self.display
        if self.scope:
            qs['scope'] = self.scope
        if self.state:
            qs['state'] = self.state
            
        qs = urllib.urlencode(qs)
        uri = '%s?%s' %(self.authorize_uri, qs)

        return uri

    def get_access_token(self, authorization_code):
        qs = {
            "client_id": self.apikey,
            "client_secret": self.apikey_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
            "code": authorization_code,
        }
        qs = urllib.urlencode(qs)
        resp, content = httplib2_request(self.access_token_uri, "POST", body=qs)
        if resp.status != 200:
            raise OAuthLoginError('get_access_token, status=%s:reason=%s:content=%s' \
                    %(resp.status, resp.reason, content))
        return json_decode(content)

class DoubanLogin(OAuth2Login):
    provider = config.OPENID_DOUBAN   

    authorize_uri = 'https://www.douban.com/service/auth2/auth'
    access_token_uri = 'https://www.douban.com/service/auth2/token' 
    user_info_uri = 'https://api.douban.com/v2/user/~me'

    def __init__(self, apikey, apikey_secret, redirect_uri, 
            scope=None, state=None, display=None):
        super(DoubanLogin, self).__init__(apikey, apikey_secret, redirect_uri, scope)

    def get_user_info(self, access_token, uid=None):
        headers = {"Authorization": "Bearer %s" % access_token}     
        qs = {
            "alt":"json",
        }
        uri = "%s?%s" %(self.user_info_uri, urllib.urlencode(qs))
        resp, content = httplib2_request(uri, "GET", 
                headers = headers)
        if resp.status != 200:
            raise OAuthLoginError('get_access_token, status=%s:reason=%s:content=%s' \
                    %(resp.status, resp.reason, content))
        r = json_decode(content)
        user_info = DoubanUser(r)

        return r

class OAuthLoginError(Exception):
    def __init__(self, msg):
        # if isinstance(msg, TweepError):
        #     self.msg = "%s:%s" %(msg.reason, msg.response) 
        # else:
        #     self.msg = msg
        self.msg = msg

    def __str__(self):
        return "%s" % (self.msg,)
    __repr__ = __str__

#-----
try:
    import json
    assert hasattr(json, "loads") and hasattr(json, "dumps")
    _json_decode = json.loads
    _json_encode = json.dumps
except Exception:
    try:
        import simplejson
        _json_decode = lambda s: simplejson.loads(_unicode(s))
        _json_encode = lambda v: simplejson.dumps(v)
    except ImportError:
        try:
            # For Google AppEngine
            from django.utils import simplejson
            _json_decode = lambda s: simplejson.loads(_unicode(s))
            _json_encode = lambda v: simplejson.dumps(v)
        except ImportError:
            def _json_decode(s):
                raise NotImplementedError(
                    "A JSON parser is required, e.g., simplejson at "
                    "http://pypi.python.org/pypi/simplejson/")
            _json_encode = _json_decode
#----

def json_decode(value):
    """Returns Python objects for the given JSON string."""
    return _json_decode(to_basestring(value))

_BASESTRING_TYPES = (basestring, type(None))
def to_basestring(value):
    """Converts a string argument to a subclass of basestring.

    In python2, byte and unicode strings are mostly interchangeable,
    so functions that deal with a user-supplied argument in combination
    with ascii string constants can use either and should return the type
    the user supplied.  In python3, the two types are not interchangeable,
    so this method is needed to convert byte strings to unicode.
    """
    if isinstance(value, _BASESTRING_TYPES):
        return value
    assert isinstance(value, bytes)
    return value.decode("utf-8")


class Douban:
    def GET(self):
        data = web.input()
        
        if data.has_key('code'):
            code = data.code
            provider = 'douban'
            d = config.APIKEY_DICT.get(provider)

            login_service = None
            if provider == config.OPENID_DOUBAN:
                openid_type = config.OPENID_TYPE_DICT[config.OPENID_DOUBAN]
                login_service = DoubanLogin(d['key'], d['secret'], d['redirect_uri'])
            # elif provider == config.OPENID_SINA:
            #     openid_type = config.OPENID_TYPE_DICT[config.OPENID_SINA]
            #     login_service = SinaLogin(d['key'], d['secret'], d['redirect_uri'])
            # else:
            #     ## 处理以oauth1的方式授权的
            #     if provider == config.OPENID_QQ:
            #         user = _qqweibo_callback(request)

            #     elif provider == config.OPENID_TWITTER:
            #         user = _twitter_callback(request)

            #     if user:
            #         _add_sync_task_and_push_queue(provider, user)
            #         return redirect(url_for('index'))
            #     else:
            #         return "connect to %s fail" % provider

            try:
                token_dict = login_service.get_access_token(code)
            except OAuthLoginError, e:
                return view.error404('Connection failed') #note:need to change view name "error404"

            if not ( token_dict and token_dict.get("access_token") ):
                return(401, "no_access_token")
            try:
                user_info = login_service.get_user_info(
                    token_dict.get("access_token"), token_dict.get("uid"))
            except OAuthLoginError, e:
                return(401, e.msg)

            if user_info:
                douban_id = user_info['id']
                nickname = user_info[u'name']
                avatarPath = user_info['avatar']

                #判断邮箱激活表中是否有此豆瓣ID
                if users.douban_id_exist_in_table_confirm_email(douban_id):
                    #如果此用户填写过email
                    if users.get_confirm_email_by_douban_id(douban_id).email:
                        info = users.get_confirm_email_by_douban_id(douban_id)
                        c = info.confirmed
                        #如果填写的邮箱已经验证
                        if c == 1:
                            #更新用户邮箱 和 昵称 等资料
                            users.update_user_by_douid(
                                douban_id,
                                nickname = nickname,
                                avatarPath = avatarPath,
                                nicknameChangeTime = datetime.datetime.now(),
                                lastLoginIP = web.ctx.ip,
                                lastLoginTime = datetime.datetime.now()
                            )
                            # last_user_id = db.query("SELECT LAST_INSERT_ID()")[0].values()[0]

                            last_user_id = users.get_douban_user_by_doubanid(douban_id).id
                            
                            try:
                                city = user_info['loc_name']
                            except Exception, e:
                                city = None

                            try:
                                desc = user_info['desc']
                            except:
                                desc = None

                            users.update_profile(last_user_id, city = city, bio = desc )

                            session.douban_login(douban_id)
                            raise web.seeother(session.get_last_visited_url())
                        elif c == 0:
                            session.douban_callback(user_info)
                            #返回 提醒用户需要激活邮件 的页面
                            raise web.seeother('/welcome/'+ user_info['uid'] +'/send_email_feedback?status=succesful')

                    #如果没填写email
                    else:
                        session.douban_callback(user_info)
                        #删除表中的记录 为了一会儿重新insert
                        users.del_verification_data_by_douban_id(douban_id)
                        #跳转到邮箱设置页面
                        raise web.seeother('/welcome/'+ user_info['uid'])

                #如果是新用户
                else:
                    session.douban_callback(user_info)
                    #跳转到邮箱设置页面
                    raise web.seeother('/welcome/'+ user_info['uid'])

                # #判断用户表中是否已有此douban_id：如果已经存在此用户
                # if users.get_douban_user_by_doubanid(douban_id):
                #     print '1111111111111111'
                #     douban_user = users.get_douban_user_by_doubanid(douban_id)

                #     #如果已经填写了邮箱地址
                #     if douban_user.email:
                #         print '222222222222'
                #         email = douban_user.email
                #         #查询邮箱验证记录
                #         e = users.get_confirm_email_by_email(email).get('confirmed')

                #         #已验证邮箱，登录
                #         if e == 1:
                #             print '33333333333333'
                #             session.douban_login(douban_id)
                #             raise web.seeother(session.get_last_visited_url())

                #         #未验证邮箱,跳转到邮箱验证页面
                #         elif e == 0:
                #             print '4444444444444444'
                #             #先把user_info信息放到 session 中，供跳转后取出使用
                #             session.douban_callback(user_info)
                #             raise web.seeother('/welcome/'+ user_info['uid'] +'confirm_email')

                #     #如果未填写邮箱地址
                #     else:
                #         print '55555555555555'
                #         #先把user_info信息放到 session 中，供跳转后取出使用
                #         session.douban_callback(user_info)
                #         #跳转到邮箱设置页面
                #         raise web.seeother('/welcome/'+ user_info['uid'])

                # #如果用户表中没有此用户
                # else:
                #     #先把user_info信息放到 session 中，供跳转后取出使用
                #     session.douban_callback(user_info)
                #     #跳转到邮箱设置页面
                #     raise web.seeother('/welcome/'+ user_info['uid'])
            else:
                return view.error404('Connection failed')
        else:
            return view.error404('Connection failed')

#connect_douban
class connect_douban:
    def GET(self):
        provider = 'douban'
        d = config.APIKEY_DICT.get(provider)
        raise web.seeother('https://www.douban.com/service/auth2/auth?client_id='+ d['key'] +'&redirect_uri='+ d['redirect_uri'] +'&response_type=code')

## User数据接口
class AbsUserData(object):

    def __init__(self, data):
        if data:
            self.data = data
        else:
            self.data = {}
        if isinstance(data, basestring):
            self.data = json_decode(data)

    def get_user_id(self):
        raise NotImplementedError

    def get_uid(self):
        raise NotImplementedError

    def get_nickname(self):
        return ""

    def get_intro(self):
        return ""

    def get_signature(self):
        return ""

    def get_avatar(self):
        return ""

    def get_icon(self):
        return ""
    
    def get_email(self):
        return ""

## 豆瓣user数据接口
class DoubanUser(AbsUserData):
    def __init__(self, data):
        super(DoubanUser, self).__init__(data)

    def get_user_id(self):
        id_ = self.data.get("id", {}).get("$t")
        if id_:
            return (id_.rstrip("/").split("/"))[-1]
        return None

    def get_uid(self):
        return self.data.get("uid", {}).get("$t")

    def get_nickname(self):
        return self.data.get("title", {}).get("$t")

    def get_intro(self):
        return self.data.get("content", {}).get("$t")

    def get_signature(self):
        return self.data.get("signature", {}).get("$t")

    def get_avatar(self):
        icon = self.get_icon()
        user_id = self.get_user_id()

        return icon.replace(user_id, "l%s" % user_id)

    def get_icon(self):
        links = {}
        _links = self.data.get("link", [])
        for x in _links:
            rel = x.get("@rel")
            links[rel] = x.get("@href")
        return links.get("icon", "")
