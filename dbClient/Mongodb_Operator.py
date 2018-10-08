# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     Mongodb_Operator
   Description : 原mongodb的数据存储
   Author :       ZWZ
   date：          18-5-10
-------------------------------------------------
   Change Activity:
                   18-5-10:
-------------------------------------------------
"""
from enum import unique

from apscheduler.schedulers import background

from utils.LogUtil import Log

__author__ = 'ZWZ'

import pymongo


# from pymongo import MongoClient

class Mongodb_Operator():
    def __init__(self, host, port, db_name, default_collection):
        Log.i('Init MongoDB')
        self.client = pymongo.MongoClient(host=host,
                                          port=port,connect=False)  # Connection() 和 MongoClient() safe MongoClient被设计成线程安全、可以被多线程共享的
        self.db = self.client.get_database(db_name)
        self.collection = self.db.get_collection(default_collection)

    def insert(self, item, collection_name=None):
        if collection_name != None:
            collection = self.db.get_collection(collection_name)
            try:
                return len(collection.insert(item))
            except Exception:
                return 0
        else:
            try:
                return len(self.collection.insert(item))
            except Exception as e:
                Log.e("mongo insert failed -> " + str(e))
                return 0

    def find(self, expression=None, collection_name=None):
        if collection_name != None:
            collection = self.db.get_collection(collection_name)
            if expression == None:
                return collection.find()
            else:
                return collection.find(expression)
        else:
            if expression == None:
                return self.collection.find()
            else:
                return self.collection.find(expression)

    def remove(self, expression=None, collection_name=None):
        if collection_name != None:
            collection = self.db.get_collection(collection_name)
            if expression == None:
                return collection.remove()
            else:
                return collection.remove(expression)
        else:
            if expression == None:
                return self.collection.remove()
            else:
                return self.collection.remove(expression)

    def findone(self, expression=None, collection_name=None):
        if collection_name != None:
            collection = self.db.get_collection(collection_name)
            if expression == None:
                return collection.find_one()
            else:
                return collection.find_one(expression)
        else:
            if expression == None:
                return self.collection.find_one()
            else:
                return self.collection.find_one(expression)

    def setunique(self, attribute, collection_name):
        if collection_name != None:
            collection = self.db.get_collection(collection_name)
            collection.create_index(attribute, unique=True)

    def ensure_index(self, key, collection_name):
        collection = self.db.get_collection(collection_name)
        collection.ensure_index(key, deprecated_unique=None)  # TODO http://ju.outofmemory.cn/entry/141346
        # https://blog.csdn.net/qq_16272049/article/details/72597870
        # collection.ensure_index(key, unique=True)

    def close_conn(self):
        """
        关闭数据库链接
        :return: 无返回值
        """
        if self.client:
            self.client.close()
            Log.d('closed mongo connection')

    # def __del__(self):
    #     '''
    #     析构方法
    #     :return: 无
    #     '''
    #     self.close_conn()



