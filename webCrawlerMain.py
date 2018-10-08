# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     Main
   Description :主入口程序
   Author :       ZWZ
   date：          18-5-9
-------------------------------------------------
   Change Activity:
                   18-5-9:
-------------------------------------------------
"""

from multiprocessing import Manager

from multiprocessing import Pipe

from Schedule.ConsumerUrl import ConsumerUrl
from Schedule.Downloader import Downloader
from utils.TimeUtil import TimeUtil

__author__ = 'ZWZ'

#URL待爬取队列
# queueDictData = Manager().Queue()
#URL管道,创建双向管道
pipeDictData = Pipe()
def run():

    p_list = list()
    consumerProcess = ConsumerUrl("consumer",pipeDictData[0])
    downloaderProcess = Downloader("downloader", pipeDictData[1])

    p_list.append(consumerProcess)
    p_list.append(downloaderProcess)

    start = TimeUtil.getDefaultTimeIt()

    for p in p_list:
        #python不允许子进程的子进程守护
        # p.daemon = True
        p.start()
    for p in p_list:
        p.join()

    end = TimeUtil.getDefaultTimeIt()
    print('parentPid run for %.2fm' %(end - start))

if __name__ == '__main__':
    #项目入口
    while True:
        run()

    sys.exit(0)