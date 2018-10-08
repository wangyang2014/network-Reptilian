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
from conf.Setting import crawlerStartTime
from test.localKafkaUrlinformation import localKafkaUrlinformation

__author__ = 'ZWZ'

if __name__ == '__main__':
    KafkaOperator = localKafkaUrlinformation()
    KafkaOperator.consumerurl()


    #http://search.ccgp.gov.cn/bxsearch?searchtype=1
    # &page_index=1
    # &bidSort=0
    # &buyerName=
    # &projectId=
    # &pinMu=0
    # &bidType=1
    # &dbselect=bidx
    # &kw=
    # &start_time=2018%3A06%3A07
    # &end_time=2018%3A06%3A07
    # &timeType=6
    # &displayZone=
    # &zoneId=
    # &pppStatus=0
    # &agentName=
    # str = 'http://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index=1&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=1&dbselect=bidx&kw=&start_time=2018%3A06%3A16&end_time=2018%3A06%3A07&timeType=6&displayZone=&zoneId=&pppStatus=0&agentName='
    # # print(str)
    # print(str.split('&')[9].split('=')[1])
    # print(crawlerStartTime)
    #
    # if str.split('&')[9].split('=')[1] != crawlerStartTime:
    #     print('no')
    # else:
    #     print('yes')