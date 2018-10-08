# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     AsycThread
   Description : 异步线程,自定义并行上限数
   Author :       ZWZ
   date：          18-5-15
-------------------------------------------------
   Change Activity:
                   18-5-15:
-------------------------------------------------
"""
import threading
import time

from concurrent.futures import ThreadPoolExecutor
from conf.Setting import MAXTHREAD
from utils.LogUtil import Log

__author__ = 'ZWZ'
from threading import Thread

class AsyncThreadScanner(threading.Thread):
    tList = []#存储队列的线程
    maxThreads=MAXTHREAD#最大并发数量,可以算4核8线程最大并发数
    event = threading.Event()#事件控制超过最大线程设置的并发线程等待
    lck = threading.Lock()  # 线程锁

    def __int__(self):
        threading.Thread.__init__(self)

    def run(self):

        try:
            pass
        except Exception as e:
            Log.i("AsyncThreadScanner run exception<<"+e.message)

        # 移除线程队列
        AsyncThreadScanner.lck.acquire()
        AsyncThreadScanner.tList.remove(self)

        # 如果移除此完成的队列线程数刚好达到上限数值-1，则说明有线程在等待执行，那么我们释放event，让等待事件执行
        if len(AsyncThreadScanner.tList) == AsyncThreadScanner.maxThreads - 1:
            AsyncThreadScanner.event.set()
            AsyncThreadScanner.event.clear()

        AsyncThreadScanner.lck.release()

    def newthread(target, args, kwargs):
        AsyncThreadScanner.lck.acquire()  # 上锁
        sc = AsyncThreadScanner()
        AsyncThreadScanner.tList.append(sc)
        AsyncThreadScanner.lck.release()  # 解锁
        sc.start()

    # 将新线程方法定义为静态变量，供调用
    newthread = staticmethod(newthread)

# def async(f):
#     """
#     异步线程,注释的方式
#     :return:
#     """
#     #这里用异步请求机制会出现并发 NoneType' object has no attribute 'select'的异常
#     def wrapper(*args, **kwargs):
#         AsyncThreadScanner.lck.acquire()
#         # 如果目前线程队列超过了设定的上线则等待
#         if len(AsyncThreadScanner.tList) >= AsyncThreadScanner.maxThreads:
#             AsyncThreadScanner.lck.release()
#             AsyncThreadScanner.event.wait()  # scanner.evnt.set()遇到set事件则等待结束
#         else:
#             AsyncThreadScanner.lck.release()
#
#         AsyncThreadScanner.newthread(target=f, args=args, kwargs=kwargs)
#
#         # thr = Thread(target=f, args=args, kwargs=kwargs)
#         # thr.start()
#         # time.sleep(1)
#
#         for t in AsyncThreadScanner.tList:
#             t.join()
#
#     return wrapper


def async(f):
    """
    异步线程,注释的方式
    :return:http://lovesoo.org/analysis-of-asynchronous-concurrent-python-module-concurrent-futures.html
    """
    #这里用异步请求机制会出现并发 NoneType' object has no attribute 'select'的异常
    def wrapper(*args, **kwargs):
        with ThreadPoolExecutor(3) as executor:
            thr = Thread(target=f, args=args, kwargs=kwargs)
            thr.start()
            #submit每次都需要提交一个目标函数和对应的参数，map只需要提交一次目标函数，目标函数的参数放在一个迭代器（列表，字典）里
            #map可以保证输出的顺序, submit输出的顺序是乱的
            executor.submit(thr)
            # executor.map(thr)
            # time.sleep(1)

    return wrapper