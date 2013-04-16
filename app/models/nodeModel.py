#!/usr/bin/env python
# coding: utf-8

import web
# import socket
from config import db

#节点入库
def newNode(nodeImg, nodeName, nodeDesc, nodeOpen, nodeCreater):

    if not nodeOpen:
        nodeOpen = '0'
    else:
        nodeOpen = '1'

    db.insert('_node', nodeImg=nodeImg, nodeName=nodeName, nodeDesc=nodeDesc, nodeOpen=nodeOpen, node_author=nodeCreater)

#得到刚创建的话题节点
def getThisNodeByUserId(nodeCreater):
    return web.listget(
        db.select('_node', vars=dict(node_author=nodeCreater), order='id DESC',
            where='node_author = $node_author'), 0, {})

#得到某一个话题节点
def getNodeByNodeId(NodeId):
    return web.listget(
        db.select('_node', vars=dict(id=NodeId), where='id = $id'), 0, {})

#得到多个话题节点
def getNodesByNodeId(NodeId):
    return db.select('_node', vars=dict(id=NodeId), where='id = $id')

#更新话题节点
# def nodeUpdate(arg, nodeImg, nodeName, nodeDesc, nodeOpen):
def nodeUpdate(arg, **kw):
    # if not nodeOpen:
    #     nodeOpen = '0'
    # else:
    #     nodeOpen = '1'

    db.update('_node', vars=dict(id=arg), where='id = $id', **kw)

#得到最近的50个话题节点
def getLastNodes():
    return  db.select('_node', limit = 100, order='id DESC')

#得到某个用户创建的话题节点
def getCreatedNodesByUserId(node_author, offset, limit):
    return db.select('_node', order='id DESC', offset=offset, limit=limit, vars=dict(node_author=node_author), where='node_author = $node_author')
