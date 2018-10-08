# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     producerUrl
   Description : 生产者任务
   Author :       ZWZ
   date：          18-5-10
-------------------------------------------------
   Change Activity:
                   18-5-10:
-------------------------------------------------
"""
import json
import os
import random

from conf.Setting import USE_SOURCEURL_TYPE, USE_ASYNCTASK_TYPE
from kafkaClient.kafkaUrlinformation import kafkaUrlinformation
from utils.ConfigUtil import ConfigUtil

__author__ = 'ZWZ'
from utils.LogUtil import Log
import multiprocessing
import time

class ProducerUrl(multiprocessing.Process):
    def __init__(self, processName, crontab, begin, end):
        multiprocessing.Process.__init__(self)
        self.processName = processName
        self.crontab = crontab
        self.begin = begin
        self.end = end

    def run(self):
        '''
        生产进程执行，每隔60*60*60*24秒，循环读取tasks
        :return:
        '''
        Log.i ('ProducerUrl.run() in {0}'.format(time.ctime()))
        while True:
            #生产URL
            if USE_SOURCEURL_TYPE is True:
                if USE_ASYNCTASK_TYPE is True:
                    urlInformationList = ConfigUtil.readSourceListByParams(self.begin, self.end)
                else:
                    urlInformationList = ConfigUtil.readSourceList()
            else:
                urlInformationList = ConfigUtil.readTaskList()

            if urlInformationList is None:
                continue

            for urlInfor in urlInformationList:
                data = urlInfor.class2dict()
                diststrjson = json.dumps(data)
                Log.i(diststrjson)
                KafkaOperator = kafkaUrlinformation()
                KafkaOperator.producerUrl(diststrjson)

            #日执行一次不用休眠了.使用crontab定时任务驱动
            if self.crontab==1:
                os._exit(0)
            else:
                # #休眠n秒(从配置文件中读取)
                items=ConfigUtil.getItems('producerScheduler')
                interval_min = items['interval_min']
                interval_max = items['interval_max']
                seconds=random.randint(int(interval_min),int(interval_max))
                Log.i('StartProducerUrl sleep ' + str(seconds) + ' seconds')
                time.sleep(seconds)

