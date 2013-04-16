#!/usr/bin/env python
# coding: utf-8

# TODO:
# - in list view show that some comments have been left
# - cut_length with more less and tooltip
# - each grader could be assigned a unique color. His actions will then be stamped by their chosen color.
# - sessions do not clean up because of is_logged var
# - let users remove their ratings
# - very weird, lighttpd refuses mod_auth on urls of the type /application/

import web
import config
import app.controllers

from app.helpers import session
from config import view,db

class Redirect:
#Make url ending with or without '/' going to the same class.
    def GET(self, path):
        web.seeother('/' + path)

def notfound():
    # return web.notfound("Sorry, the page you were looking for was not found.")
    # You can use template result like below, either is ok:
    return web.notfound(view.error())
    #return web.notfound(str(render.notfound()))

def internalerror():
    return web.InternalError(view.error500())


urls = (
    '/(.*)/',                                      'Redirect',
    # '/submit_application',                       'app.controllers.submit_application.apply',
    # '/submit_reference/([0-9a-f]{32})',          'app.controllers.submit_reference.refer',
    # '/affiliated/submit_application',            'app.controllers.submit_application.apply_simple',
    
    # '/(|new|pending|all|admitted)',              'app.controllers.browse.list',
    # '/(search|rejected|reviewed)',               'app.controllers.browse.list',
    # '/applicant/(\d+)',                          'app.controllers.browse.show',
    
    # '/admit',                                    'app.controllers.actions.admit',
    # '/reject',                                   'app.controllers.actions.reject',
    # '/undecide',                                 'app.controllers.actions.undecide',
    # '/rate',                                     'app.controllers.actions.rate',
    
    # '/applicant/(\d+)/comment',                  'app.controllers.actions.comment',
    # '/delete_comment/(\d+)',                     'app.controllers.actions.delete_comment',
    
    # '/grant/(\d+)',                              'app.controllers.actions.grant',

    '/',                                                        'app.controllers.home.index',
    '/node',                                                    'app.controllers.home.rec_node',
    # '/explore',                                                 'app.controllers.home.explore',

#account
    # '/account/register',                                        'app.controllers.account.register',
    # '/account/login',                                           'app.controllers.account.login',
    '/account/logout',                                          'app.controllers.account.logout',
    # '/account/forgot',                                          'app.controllers.account.forgot',
    # '/account/reset/([0-9a-zA-Z]{32})',                         'app.controllers.account.reset',
    # '/account/help',                                            'app.controllers.account.help',
    # '/account/check_username',                                  'app.controllers.account.check_username',
    '/account/check_email',                                     'app.controllers.account.check_email',
    # '/account/landing_login',                                   'app.controllers.account.landing_login',
    # '/account/landing_forgot',                                  'app.controllers.account.landing_forgot',
    # '/account/confirm/([0-9a-z]{32})',                          'app.controllers.account.confirm_email',
    '/account/apply_for_permission',                              'app.controllers.account.apply_for_permission',

#welcome
    '/welcome/([a-zA-Z0-9][\w\-\.\_]+)',                          'app.controllers.welcome.welcome',
    '/welcome/([a-zA-Z0-9][\w\-\.\_]+)/send_email_feedback',      'app.controllers.welcome.send_email_feedback',
    '/welcome/confirm_email/([0-9a-z]{32})',                      'app.controllers.welcome.welcome_confirm_email',

#settings
    '/settings',                                                   'app.controllers.settings.index',
    #note '/settings/avatar',                                         'app.controllers.settings.member_avatar',
    #note '/settings/avatar_crop',                                    'app.controllers.settings.member_avatar_crop',
    '/settings/change_email',                                          'app.controllers.settings.change_email',
    #note '/settings/password',                                       'app.controllers.settings.change_password',
    #note '/settings/nickname',                                       'app.controllers.settings.change_nickname',
    '/settings/email_subscribe',                                      'app.controllers.settings.email_subscribe',

    #'/settings/password_check_password',                        'app.controllers.settings.check_password',
    
    #'/(?:img|js|css|swf)/.*',                                   'app.controllers.public.public',

#member
    '/member/([a-zA-Z0-9][\w\-\.\_]+)',                                 'app.controllers.member.member_home',
    '/member/([a-zA-Z0-9][\w\-\.\_]+)/page/(\+?[1-9][0-9]*)',           'app.controllers.member.member_home_post_load_more',
    # '/member/([a-zA-Z0-9][\w\-\.\_]+)/favorite',                      'app.controllers.member.member_favorite',
    '/member/([a-zA-Z0-9][\w\-\.\_]+)/node',                            'app.controllers.member.member_node',
    '/member/([a-zA-Z0-9][\w\-\.\_]+)/node/page/(\+?[1-9][0-9]*)',      'app.controllers.member.member_home_node_load_more',
    '/member/([a-zA-Z0-9][\w\-\.\_]+)/node/contributed',                'app.controllers.member.contributed_node',
    '/member/([a-zA-Z0-9][\w\-\.\_]+)/node/contributed/page/(\+?[1-9][0-9]*)', 'app.controllers.member.contributed_node_more',


#media
    '/media/upload',                                            'app.controllers.media.media_upload',
    '/media/describe',                                          'app.controllers.media.media_describe',
    '/photo/([0-9]{8})',                                        'app.controllers.media.photo_single',
    '/photo/edit/([0-9]{8})',                                   'app.controllers.media.photo_edit',
    '/photo/([0-9]{8})/fans',                                   'app.controllers.media.photo_fans',
    '/photo/delete/([0-9]{8})',                                 'app.controllers.media.photo_delete',
    '/photo/favorite/([0-9]{8})',                               'app.controllers.media.photo_favorite',
    '/photo/cancel_fav/([0-9]{8})',                             'app.controllers.media.photo_cancel_favorite',
    '/photo/([0-9]{8})/comment',                                'app.controllers.media.photo_add_comment',
    '/photo/delete_comment',                                    'app.controllers.media.photo_del_comment',

#node
    '/node/new',                                                'app.controllers.node.new_node',
    '/node/all',                                                'app.controllers.node.node_all',
    '/node/(\+?[1-9][0-9]*)',                                   'app.controllers.node.node_show',#验证非零的正整数
    '/node/(\+?[1-9][0-9]*)/recent',                            'app.controllers.node.node_recent', #按时间排序
    '/node/(\+?[1-9][0-9]*)/recent/page/(\+?[1-9][0-9]*)',      'app.controllers.node.node_load_more',
    '/node/(\+?[1-9][0-9]*)/page/(\+?[1-9][0-9]*)',             'app.controllers.node.node_load_more',
    '/node/(\+?[1-9][0-9]*)/update',                            'app.controllers.node.node_update',
    '/node/node_image',                                         'app.controllers.node.node_image',
    '/node/delete_node_image',                                  'app.controllers.node.delete_node_image',

#post
    '/node/(\+?[1-9][0-9]*)/post',                              'app.controllers.post.new_post',
    '/post/post_image_upload',                                  'app.controllers.post.post_image_upload',
    # '/post/post_image_upload_2',                                'app.controllers.post.post_image_upload_2',
    '/post/post_image_delete',                                  'app.controllers.post.post_image_delete',
    '/post/(\+?[1-9][0-9]*)',                                   'app.controllers.post.post_single',
    '/post/(\+?[1-9][0-9]*)/edit',                              'app.controllers.post.post_edit',
    '/post/post_image_update',                                  'app.controllers.post.post_image_update',
    '/post/(\+?[1-9][0-9]*)/post_title_update',                 'app.controllers.post.post_title_update',
    '/post/(\+?[1-9][0-9]*)/post_field_update',                 'app.controllers.post.post_field_update',
    '/post/vote',                                               'app.controllers.post.post_vote',
    '/post/vote_cancel',                                        'app.controllers.post.vote_cancel',
    '/post/latest',                                             'app.controllers.post.post_latest',

#post_comment
    '/post/(\+?[1-9][0-9]*)/new_comment',                       'app.controllers.post.new_post_comment',
    '/post/delete_comment',                                     'app.controllers.post.del_post_comment',

#notification
    '/notification/make_read',                                   'app.controllers.notification.make_single_read',
    '/notification/make_all_read',                              'app.controllers.notification.make_all_read',

#misc
    # '/tests/session',                                           'app.tests.session',
    # '/tests/upload',                                            'app.tests.upload',

    # '/test',                                                    'app.controllers.home.checkcode',

#connect
    '/connect/douban',                                          'app.controllers.sns.connect_douban',
    '/connect/douban/callback',                                 'app.controllers.sns.Douban',

#helper
    '/clearPhoto',                                              'tools.clearPhoto',

#admin
    '/admin',                                                   'app.controllers.admin.home',
    '/admin/rec_node',                                          'app.controllers.admin.rec_node',
    '/admin/rec_post',                                          'app.controllers.admin.rec_post',
    '/admin/rec_post/save_sort',                                'app.controllers.admin.save_sort',
    '/admin/rec_post/del_rec_post',                             'app.controllers.admin.del_rec_post',
    '/admin/rec_post/del_rec_node',                             'app.controllers.admin.del_rec_node',
    '/admin/users',                                             'app.controllers.admin.admin_users',
    '/admin/change_user_rights',                                'app.controllers.admin.change_user_rights',
    '/admin/users/del_users',                                   'app.controllers.admin.del_users',
    '/admin/apply_for_permission',                              'app.controllers.admin.apply_for_permission',
    '/admin/apply_operate',                                     'app.controllers.admin.apply_operate',
    '/admin/feedback',                                          'app.controllers.admin.feedback',

#pages
    '/update',                                                  'app.controllers.pages.update',
    '/about',                                                   'app.controllers.pages.about',
    '/policy',                                                  'app.controllers.pages.policy',
    '/guideline',                                               'app.controllers.pages.guideline',
    '/privacy',                                                 'app.controllers.pages.privacy',
    '/blog',                                                    'app.controllers.pages.blog',

    '/api',                                                    'app.controllers.api.index',
#help
    '/help/feedback',                                           'app.controllers.help.feedback',

    # '/api',                                                    'app.controllers.api.index',

)

app = web.application(urls, globals())

if web.config.email_errors:
    app.internalerror = web.emailerrors(web.config.email_errors, web.webapi._InternalError)

web.config.session_parameters['cookie_name'] = '_u0i_ej3eu932j'

# ==============Online Product:==============
#web.config.session_parameters['cookie_domain'] = '.biubiubiubiu.com'
# ==============Product Dev:==============
#web.config.session_parameters['cookie_domain'] = '.biu.com'
#==============Local Dev:==============
web.config.session_parameters['cookie_domain'] = '.biubiu.com'

web.config.session_parameters['timeout'] = 86400*30  #24 * 60 * 60, # 24 hours   in seconds
web.config.session_parameters['ignore_expiry'] = False
web.config.session_parameters['ignore_change_ip'] = True
web.config.session_parameters['secret_key'] = 'fLjUfxqXtfNoIldA0A0J'
web.config.session_parameters['expired_message'] = 'session已过期'

#hack debug session bug http://webpy.org/cookbook/session_with_reloader.zh-cn
session.add_sessions_to_app(app)

class SessionExpired(web.HTTPError):
    def __init__(self, message):
        message = web.seeother('/')
        web.setcookie('_u0i_ej3eu932j', '' , -1)
        web.HTTPError.__init__(self, '303 See Other', {}, data=message)
        # web.HTTPError.__init__(self, '200 ok', {}, data=message)

web.session.SessionExpired = SessionExpired 

if __name__ == "__main__":
    #==============Local Dev:==============
    # web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    app.notfound = notfound
    app.internalerror = internalerror
    app.run()