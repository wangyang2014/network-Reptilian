# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     InitUtil
   Description : 快速初始化数据库(慎用，这个是用来清理LOG的数据库，禁止拿来清理数据源)
   Author :       ZWZ
   date：          18-5-10
-------------------------------------------------
   Change Activity:
                   18-5-10:
-------------------------------------------------
"""
__author__ = 'ZWZ'


from utils.MongoUtil import MongoUtil
import conf.Setting as Setting

class InitUtil:
    '''
    初始化，清空所有数据，重新开始新一轮任务
    '''
    def __init__(self):
        self.mongoUtil = MongoUtil()
        pass

    def init(self):
        db = Setting.MONGO_DB
        self.mongoUtil.clear_all(db)

    def __del__(self):
        self.mongoUtil.close_conn()

if __name__ == '__main__':
    input = input('clear all data, really? (y/n):')
    if input.lower()=='y':
        initUtil=InitUtil()
        initUtil.init()
        print('all data clear finished')
    else:
        print('Noting be clear, bye!')
    #设置全局标志，让死循环的Log线程退出
    setattr(Setting,'exit_flag',True)