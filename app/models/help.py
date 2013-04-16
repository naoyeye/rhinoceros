#!/usr/bin/env python
# coding: utf-8

import web
from config import db

#保存用户反馈
def save_feedback(content, douban_id):
    db.insert('_feedback', douban_id=douban_id, content=content)


# 分页
def query(query=None, offset=10, limit=10, order='id desc'):
    table = '_feedback'
    results = db.select(table, 
        offset = offset,
        limit = limit,
        order = order)

    count = int(db.select(table, what='count(distinct id) as c')[0].c)
    
    return (results, count)