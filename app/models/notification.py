#!/usr/bin/env python
# coding: utf-8

import web
from config import db

#新增提醒
def new_notification(aid, uid, pid, nid, tp):
    db.insert('_notification', aid=aid, uid=uid, pid=pid, nid=nid, type=tp)

#新增@提醒
def new_mention_notification(pid, nid, aid, uid, mid):
    db.insert('_notification_mention', pid=pid, nid=nid, aid=aid, uid=uid, mid=mid)

#得到提醒数
def get_unread_notification(uid):
    getwhere = 'aid = $uid and isread = 0'
    notification_results = db.select('_notification', vars=dict(uid=uid), where=getwhere, order='id DESC')
    count = int(db.select('_notification', what='count(distinct id) as c', where=getwhere, vars=dict(uid=uid))[0].c)
    return (notification_results, count)

#得到@提醒
def get_unread_metion_notifition(uid):
    getwhere = 'mid = $uid and isread = 0'
    notification_mention_results = db.select('_notification_mention', vars=dict(uid=uid), where=getwhere, order='id DESC')
    count_mention = int(db.select('_notification_mention', what='count(distinct id) as c', where=getwhere, vars=dict(uid=uid))[0].c)
    return (notification_mention_results, count_mention)

#设为已读
def make_single_read(id, uid):
    db.update('_notification', vars=dict(id=id, aid=uid), where='id = $id and aid=$aid', isread=1)
    db.update('_notification_mention', vars=dict(id=id, mid=uid), where='id = $id and mid=$mid', isread=1)

#全部设为已读
def make_all_read(id_list, uid):
    for id in id_list:
        db.update('_notification', vars=dict(id=id, aid=uid), where='id = $id and aid=$aid', isread=1)
        db.update('_notification_mention', vars=dict(id=id, mid=uid), where='id = $id and mid=$mid', isread=1)

