# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyIpPool
   Description : 获取免费代理IP池
   Author :       ZWZ
   date：          18-5-13
-------------------------------------------------
   Change Activity:
                   18-5-13:
-------------------------------------------------
"""
from proxyClient.proxyClient import getIpProxyPool, getIpProxyPoolFromeRemote

__author__ = 'ZWZ'

import json
import random
import sys
from utils.ConfigUtil import ConfigUtil

__author__ = 'ZWZ'
from utils.LogUtil import Log
import multiprocessing
import time


class ProxyIpPool(multiprocessing.Process):
    def __init__(self, processName, queueDictData):
        multiprocessing.Process.__init__(self)
        self.processName = processName
        self.queueDictData = queueDictData

    def run(self):
        '''
        获取免费IP代理进程执行，循环读取tasks
        :return:
        '''
        Log.i('proxyIpPool.run() in {0}'.format(time.ctime()))
        while True:
            #调用本地和远程的免费ip代理api并推进ip消息队列
            proxyIpPool = getIpProxyPool()
            #统一改成本地
            proxyIpPoolFromeRemote = getIpProxyPool()
            # proxyIpPoolFromeRemote = getIpProxyPoolFromeRemote()
            if proxyIpPool is not None:
                self.queueDictData.put(proxyIpPool)
            if proxyIpPoolFromeRemote is not None:
                self.queueDictData.put(proxyIpPoolFromeRemote)
            # 休眠n秒(从配置文件中读取)
            items = ConfigUtil.getItems('proxyIpScheduler')
            interval_min = items['interval_min']
            interval_max = items['interval_max']
            seconds = random.randint(int(interval_min), int(interval_max))
            Log.i('proxyIpPool sleep ' + str(seconds) + ' seconds')
            time.sleep(seconds)

