# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     kafkaConf
   Description :
   Author :       ZWZ
   date：          18-6-15
-------------------------------------------------
   Change Activity:
                   18-6-15:
-------------------------------------------------
"""
__author__ = 'ZWZ'

##############
# KafKa本地配置
##############
localKafka_setting = {
    'bootstrap_servers': ["10.0.0.32:9092"],
    'topic_name': 'ailongma_analysis_ccgp',
    'topic_name_ccgp': 'ailongma_analysis_ccgp_realtime',
    'consumer_id': 'CID_alikafka_ailongma_G1'
}