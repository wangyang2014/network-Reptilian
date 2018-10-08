# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testKafka
   Description :
   Author :       ZWZ
   date：          18-6-15
-------------------------------------------------
   Change Activity:
                   18-6-15:
-------------------------------------------------
"""
import json

from test.localKafkaUrlinformation import localKafkaUrlinformation
from utils.LogUtil import Log

__author__ = 'ZWZ'

if __name__ == '__main__':
    KafkaOperator = localKafkaUrlinformation()
    for i in range(0, 10):
        KafkaOperator.producerUrl(str(i))
