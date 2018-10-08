# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     TimeUtil
   Description :时间处理工具类
   Author :       ZWZ
   date：          18-5-10
-------------------------------------------------
   Change Activity:
                   18-5-10:
-------------------------------------------------
"""
__author__ = 'ZWZ'

import time
import timeit

class TimeUtil:

    @staticmethod
    def getFormatTime(strFormat):
        return time.strftime(strFormat,time.localtime(time.time()))

    @staticmethod
    def getDefaultTimeIt():
        """
        跨平台的精度性
        :return:timeit.default_timer()单位是秒  print('ran for %.2fm' %((1.33 - 0.333)/60))
        """
        return timeit.default_timer()