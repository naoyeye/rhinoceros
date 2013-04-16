#!/usr/bin/env python
# coding: utf-8

import datetime
import web
from config import db, view
from app.models import postModel, nodeModel, users

class index_feed:
    def GET(self):
        date = datetime.datetime.today().strftime("%a, %d %b %Y %H:%M:%S +0200")
        rec_posts = list(db.select('_admin_rec_home', where='pid', order="pid_sort"))

        postList = []
        for i in xrange(len(rec_posts)):
            postList += postModel.getPostsByPostId(rec_posts[i].pid)

        authors = []
        for i in xrange(len(postList)):
            authors += users.get_users_by_id(postList[i].postAuthor)

        nodes = []
        for i in xrange(len(postList)):
            nodes += nodeModel.getNodesByNodeId(postList[i].nodeId)

        feed_url="http://www.biubiubiubiu.com/feed"

        ishome = True
        node = None

        web.header('Content-Type', 'application/xml')

        return view.feed_index(node, postList, date, authors, nodes, feed_url, ishome)

class node_feed:
    def GET(self, nodeId):
        date = datetime.datetime.today().strftime("%a, %d %b %Y %H:%M:%S +0200")
        node = nodeModel.getNodeByNodeId(nodeId)
        posts = list(db.select("_post", order="id DESC", limit=10, vars=dict(nodeId=nodeId), where='nodeId = $nodeId'))
        authors = []
        for i in xrange(len(posts)):
            authors += users.get_users_by_id(posts[i].postAuthor)

        nodes = []
        for i in xrange(len(posts)):
            nodes += nodeModel.getNodesByNodeId(posts[i].nodeId)

        feed_url="http://www.biubiubiubiu.com/'+ nodeId +'feed"

        ishome = False

        web.header('Content-Type', 'application/xml')
        return view.feed_index(node, posts, date, authors, nodes, feed_url, ishome)