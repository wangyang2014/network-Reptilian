# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ProducerMain
   Description :生产根域名主入口文件(使用crontab定时任务)
   Author :       ZWZ
   date：          18-5-15
-------------------------------------------------
   Change Activity: 命令行启动=>python3 ProducerMain.py 0 4 7;crontab启动=>python3 ProducerMain.py 1
                   18-5-15:
-------------------------------------------------
"""
import os
import sys

from Schedule.simpleProducerChildUrl import simpleProducerChildUrl
from utils.LogUtil import Log
from utils.TimeUtil import TimeUtil

__author__ = 'ZWZ'


if __name__ == '__main__':
    crontab = 0
    #项目入口
    producerChildUrl = simpleProducerChildUrl("producer", crontab)
    producerChildUrl.simpleRun()
