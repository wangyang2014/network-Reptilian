# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ConsumerUrl
   Description :消费者任务下发
   Author :       ZWZ
   date：          18-5-10
-------------------------------------------------
   Change Activity:
                   18-5-10:
-------------------------------------------------
"""
import random
from multiprocessing import Process

from kafkaClient.localKafkaUrlinformation import localKafkaUrlinformation
from utils.ConfigUtil import ConfigUtil
from utils.LogUtil import Log

__author__ = 'ZWZ'

import multiprocessing
import time

class ConsumerUrl(multiprocessing.Process):
    def __init__(self, processName, pipeDictData):
        multiprocessing.Process.__init__(self)
        self.processName = processName
        self.pipeDictData = pipeDictData

    @staticmethod
    def run_kafkaConsumerListener(pipeDictData):
        """
        消费者监听URL生成事件驱动器
        :param queueDictData: 源数据队列
        """
        KafkaOperator = localKafkaUrlinformation()
        #pip管道直接传进去,妈的逼消费者进程死循环
        KafkaOperator.consumerurl(pipeDictData)


    def run(self):
        '''
        KfKa消费者监听对象,任务分发下载器
        :return:
        '''
        Log.i('comsumerUrl.run() in {0}'.format(time.ctime()))
        while  True:
            #调用消费者监听器
            self.run_kafkaConsumerListener(self.pipeDictData)
            # 休眠n秒(从配置文件中读取)
            items=ConfigUtil.getItems('consumerScheduler')
            interval_min = items['interval_min']
            interval_max = items['interval_max']
            seconds=random.randint(int(interval_min),int(interval_max))
            Log.i('StartConsumer sleep ' + str(seconds) + ' seconds')
            time.sleep(seconds)
