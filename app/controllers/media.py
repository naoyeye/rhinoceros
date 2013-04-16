#!/usr/bin/env python
# coding: utf-8

import web
import time
import datetime

from config import view, site_name, site_domain

from app.helpers import session
from app.helpers import paging

from app.models import users
from app.models import image

siteName = site_name
siteDomain = site_domain
user = session.get_session()

results_per_page = 50
default_order = 'id'

class media_upload:
    @session.login_required
    def GET(self):
        return view.media_upload(user)

    @session.login_required
    def POST(self):
        data = web.input(path={})
        paths = data.get('path').split(',')
        names = data.get('name').split(',')
        userID = user.id
        #creationTime = time.mktime(time.localtime())
        image.AddImage(paths, names, userID) #入库
        return view.base(view.media_describe(paths, names), user, siteName)

class media_describe:
    @session.login_required
    def POST(self):
        f = web.input(image_title=[],image_describe=[],path={})
        imageTitle = f.image_title
        imageDescribe = f.image_describe
        imagePath = f.path.split(',')
        username = user.username
        image.saveTitleDescribe(imagePath, imageTitle, imageDescribe) #入库
        raise web.seeother('/member/'+ username)

class photo_single:
    def GET(self, id):
        img = image.get_img_by_imgid(id)
        if img:
            i = web.input(start=0, order=default_order, desc='desc', query='')
            start = int(i.start)
            user_id = session.is_logged() and session.get_user_id()
            author_id = img.userID
            results, num_results = image.query(author_id)
            pager = web.storage(paging.get_paging_results(start, num_results, 
                int(id), results, results_per_page))
            #tm = time.strftime('%Y年%m月%d日', time.localtime(img.creationTime))
            author = users.get_user_by_id(img.userID)
            results = list(results)
            is_favorite = image.IsFavorite(user_id, img.id)

            #得到被多少人喜欢
            #count = image.GetFavUserCount(img_id)

            #浏览人数加1
            if user_id and image.user_not_viewed_image(user_id, id):
                image.add_img_hit(id)
                image.add_user_to_img_viewed(user_id, id)

            #得到评论
            comments = image.get_comment_by_image_id(id).list()
            #得到评论者信息
            comments_authors_ids = []
            for i in xrange(len(comments)):
                #comments_authors_ids += str(comments[i].user_id).split()
                comments_authors_ids += users.get_users_by_id(comments[i].user_id).list()
            

            return view.base(view.photo_single(img, pager, user_id, user, author, is_favorite, comments, comments_authors_ids), user, siteName)
        else:
            raise web.notfound()

class photo_edit:
    @session.login_required
    def POST(self,url):
        data = web.input(inputfield = {}, textfield = {})
        imageId = data.id
        imageTitle = data.inputfield
        imageDescribe = data.textfield
        image.UpdateImageTitleAndDescribe(imageId, imageTitle, imageDescribe)

class photo_delete:
    @session.login_required
    def POST(self,url):
        data = web.input(id = {})
        imageId = data.id
        userID = data.userID
        image.DeleteImageByImageID(imageId, userID)

class photo_favorite:
    @session.login_required
    def POST(self,url):
        data = web.input()
        u_id = data.user_id
        i_id = data.img_id
        image.AddFavorite(u_id, i_id)

class photo_cancel_favorite:
    @session.login_required
    def POST(self,url):
        data = web.input()
        u_id = data.user_id
        i_id = data.img_id
        image.CancelFavorite(u_id, i_id)

class photo_fans:
    def GET(self, img_id):
        img = image.get_img_by_imgid(img_id)
        author = web.listget(users.get_users_by_id(img.userID) , 0, {})

        fav_user = image.GetFavImageByImageId(img_id).list()
        fav_user_ids = []
        for i in xrange(len(fav_user)):
            fav_user_ids += str(fav_user[i].user_id).split()

        usernnames = []
        for i in xrange(len(fav_user_ids)):
            usernnames += users.get_users_by_id(fav_user_ids[i])

        return view.base(view.photo_fans(img_id, img, usernnames, author), user, siteName)

class photo_add_comment:
    @session.login_required
    def POST(self, img_id):
        data = web.input()
        i_id = data.img_id
        u_id = data.u_id
        comment = data.comment
        image.add_img_comment(comment, u_id, i_id)
        #return view.test(comment)

class photo_del_comment:
    @session.login_required
    def POST(self):
        data = web.input()
        id = data.id
        user_id = data.user_id
        img_id = data.img_id
        image.DeleteCommentByCommentID(id, user_id, img_id)