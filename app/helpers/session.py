#!/usr/bin/env python
# coding: utf-8

# Author: Alex Ksikes

# TODO:
# - webpy session module is ineficient and makes 5 db calls per urls!
# - because sessions are attached to an app, every user has sessions whether they atually need it or not.
# - login required decorator should save intended user action before asking to login.

import web
from config import db
from config import view
from app.models import users
from app.models import applicants


class Session(web.session.Session):
    def _setcookie(self, session_id, expires='', **kw):
        if expires == '':
            expires = self._config.timeout
        super(Session, self)._setcookie(session_id, expires, **kw)

def add_sessions_to_app(app):
    if web.config.get('_session') is None:
        store = web.session.DBStore(db, 'sessions')
        session = Session(app, store, 
                    initializer={'is_logged' : False})
        web.config._session = session
    else:
        session = web.config._session

def get_session():
    return web.config._session

def is_logged():
    return get_session().is_logged

def login(email):
    s = get_session()
    for k, v in users.get_user_by_email(email).items():
        s[k] = v
    s.is_logged = True

def douban_login(douban_id):
    s = get_session()
    for k, v in users.get_douban_user_by_doubanid(douban_id).items():
        s[k] = v
    s.is_logged = True
    web.setcookie('_u0i_ej3eu932j', s.session_id, expires = 3600*24*30)

def douban_callback(user_info):
    s = get_session()
    s.is_logged = False
    s.douban_id = user_info['id']
    s.username = user_info['uid']
    s.nickname = user_info['name']
    s.avatarPath = user_info['avatar']
    try:
        s.city = user_info['loc_name']
    except Exception, e:
        s.city = None

    try:
        s.desc = user_info['desc']
    except Exception, e:
        s.desc = None

def clear_douban_callback():
    s = get_session()
    s.is_logged = False
    s.douban_id = None
    s.username = None
    s.nickname = None
    s.avatarPath = None
    s.city = None
    s.desc = None

def logout():
    _session = get_session()
    web.setcookie('_u0i_ej3eu932j',_session.session_id, -1)
    _session.kill()

    
def reset():
    user = users.get_user_by_id(get_user_id())
    login(user.email)

def get_user_id():
    return get_session().id

def get_last_visited_url():
    redirect_url = web.cookies(redirect_url='/').redirect_url
    web.setcookie('redirect_url', '', -1)
    return redirect_url

# def set_last_visited_url():
#     url = web.ctx.get('path')
#     # if url:
#     #     web.setcookie('redirect_url', url)
#     # else:
#     #     web.setcookie('redirect_url', '/test')
#     return url

def login_required(meth):
    def new(*args):
        if not is_logged():
            url = web.ctx.get('path')
            web.setcookie('redirect_url', url)
            return web.redirect('/')
        return meth(*args)
    return new

def login_required_for_reviews(meth):
    def new(*l):
        context = l[1] or web.input(context='').context
        if not is_logged() and context == 'reviewed':
            return web.redirect('/')
        return meth(*l)
    return new


# def douban_login(douban_id):
#     s = get_session()
#     for k, v in users.get_douban_user_by_doubanid(douban_id).items():
#         s[k] = v
#     s.is_logged = True



