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

from Schedule.ProducerUrl import ProducerUrl
from utils.LogUtil import Log
from utils.TimeUtil import TimeUtil

__author__ = 'ZWZ'

def run():
    if sys.argv[1] is None and sys.argv[2] is None and sys.argv[3] is None:
        Log.i("no params error")
        os._exit(0)
    else:
        isCrontab = sys.argv[1]
        begin = sys.argv[2]
        end = sys.argv[3]

    #是否crontab命令启动,1代表是,其它代表否
    if isCrontab==str(1):
        crontab = 1
    else:
        crontab = 0

    p_list = list()
    producerProcess = ProducerUrl("producer", crontab, begin, end)
    p_list.append(producerProcess)

    # start = TimeUtil.getDefaultTimeIt()

    for p in p_list:
        p.daemon = True
        p.start()
    for p in p_list:
        p.join()

    # end = TimeUtil.getDefaultTimeIt()
    # Log.i('ProducerUrlParentPid run for %.2fm' %(end - start))
    if crontab==1:
        os._exit(0)

if __name__ == '__main__':

    #项目入口
    run()