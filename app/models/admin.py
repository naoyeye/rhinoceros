#!/usr/bin/env python
# coding: utf-8

import web
from config import db

#新增首页推荐话题、片段
def admin_rec_home_post(**kw):
    db.insert('_admin_rec_home', **kw)

#得到全部的推荐片段
def get_rec_posts():
    return db.select('_admin_rec_home', where='pid', order="pid_sort")

#得到全部的推荐话题
def get_rec_nodes():
    return db.select('_admin_rec_home', where='nid', order="nid_sort")

#
def save_sort(pids, nids):
    #note: 可以优化 因为有时候只是修改了node sort,post sort根本没变
    for i in xrange(len(pids)):
        db.update('_admin_rec_home', vars=dict(pid=pids[i]), where='pid = $pid', pid_sort = i+1)
    for i in xrange(len(nids)):
        db.update('_admin_rec_home', vars=dict(nid=nids[i]), where='nid = $nid', nid_sort = i+1)

#del_rec_post
def del_rec_post(pid):
    db.delete('_admin_rec_home', vars = dict(pid=pid), where = 'pid = $pid')

# del_rec_node
def del_rec_node(nid):
    db.delete('_admin_rec_home', vars = dict(nid=nid), where = 'nid = $nid')


def get_where(query=None, user_id=None):
    where = ''

    # if in search mode
    if query:
        columns = 'first_name, last_name, a.email, affiliation, department, referee_name, status, \
        occupation, website, interests'.split(', ')
        query = web.sqlquote('%%' + query.encode('utf-8') + '%%')
        
        where = (' like %s or ' % query).join(columns)
        where += ' like %s' % query
        where += ' or concat(first_name, " ", last_name) like ' + query
    
    return where

#admin_users 分页
def query(query=None, offset=8, limit=8, order='id desc', user_id=None):
    table = 'users'
    results = db.select(table, 
        offset = offset,
        limit = limit,
        order = order)

    count = int(db.select(table, what='count(distinct id) as c')[0].c)
    
    return (results, count)

#查询邮箱验证记录
def confirm_log_query(query=None, offset=8, limit=8, order='id desc', user_id=None, c='1'):
    table = '_confirm_email'

    if c == '1' or c == '':
        getwhere = 'confirmed = 1'
    elif c == '0':
        getwhere = 'confirmed = 0'
        order='email desc'

    results = db.select(table, 
        offset = offset,
        limit = limit,
        where = getwhere,
        order = order)

    count = int(db.select(table, what='count(distinct id) as c', where=getwhere)[0].c)
    
    return (results, count)
