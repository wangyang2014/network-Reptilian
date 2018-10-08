# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ConfigUtil
   Description : 配置获取工具类
   Author :       ZWZ
   date：          18-5-9
-------------------------------------------------
   Change Activity:
                   18-5-9:
-------------------------------------------------
"""
import datetime
import json

from conf.Setting import TASK_FILENAME, SOURCEURL_FILENAME, USE_BXBLS, crawlerStartTime, crawlerEndTime
from entity.URLinformation import URLinformation
from utils.UrlUtil import UrlUtil

__author__ = 'ZWZ'

import configparser
import os



class ConfigUtil(object):
    '''
    读取ini配置文件
        ini文件结构如下：
        [Section1]
        option1 : value1
        option2 : value2
    '''

    def __init__(self):
        pass

    @staticmethod
    def _getConfig():
        '''
        获取config对象
        :return: config对象
        '''
        config = configparser.ConfigParser()
        conf_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'conf', 'config.ini')
        config.read(conf_file, encoding='UTF-8')
        return config

    @staticmethod
    def readSourceListRealTime():
        """
        构造实时爬取父URL
        bidType字段:招标类型
        page_index字段:页码
        start_time=2018%3A06%3A06字段:开始时间,2018年06月06日
        end_time=2018%3A06%3A06字段:开始时间,2018年06月06日
        """
        #http://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index=1&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=1&dbselect=bidx&kw=&start_time=,
        # &end_time=,
        # &timeType=6&displayZone=&zoneId=&pppStatus=0&agentName=

        #截取今天时间
        # nowTime = datetime.datetime.now().strftime('%Y-%m-%d').split('-')
        # strNowTime = nowTime[0]+'%3A'+nowTime[1]+'%3A'+nowTime[2]
        #老罗说要爬取一周的数据
        strNowTime = crawlerStartTime
        strEndTime = crawlerEndTime
        MyUrl_SourceList = []

        ftp = open(SOURCEURL_FILENAME, 'r')
        for line in ftp.readlines():
            myUrllist = line.split(',')
            # url = myUrllist[0]+strNowTime+myUrllist[1]+strNowTime+myUrllist[2]
            url = myUrllist[0] + strNowTime + myUrllist[1] + strEndTime + myUrllist[2]
            URL_inf = URLinformation(url.strip('\n'), int(0), 0.0, float(0))  # 格式
            URL_inf.Flag = 0
            URL_inf.DeepNum = 1
            URL_inf.domain = UrlUtil.getdomain(url)
            MyUrl_SourceList.append(URL_inf)
        else:
            ftp.close()

        return MyUrl_SourceList

    @staticmethod
    def readSourceListByParams(begin, end):
        '''
        构造URL配置文件
        :return: URL LIST对象
        '''
        if USE_BXBLS is True:
            MyUrl_SourceList = []
            ftp = open(SOURCEURL_FILENAME, 'r')
            # http: // www.ccgp.gov.cn / cggg / zygg / index, 0, 0, 0, 0, 24
            # http: // www.ccgp.gov.cn / cggg / dfgg / index, 0, 0, 0, 0, 24
            for line in ftp.readlines():
                myUrllist = line.split(',')
                for i in range(int(begin), int(end)+1):  # 每个list 存到 list中
                    if i ==0:
                        url = myUrllist[0] +".htm"
                    else:
                        url = myUrllist[0] +"_"+ str(i)+".htm"

                    URL_inf = URLinformation(url, int(myUrllist[1]), 0.0, float(myUrllist[2]))  # 格式
                    URL_inf.Flag = 0
                    URL_inf.DeepNum = 1
                    URL_inf.domain = UrlUtil.getdomain(url)
                    MyUrl_SourceList.append(URL_inf)

        else:
            MyUrl_SourceList = []
            ftp = open(SOURCEURL_FILENAME, 'r')
            # http://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index=,&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=1&dbselect=bidx&kw=&start_time=2013%3A04%3A09&end_time=2014%3A04%3A08&timeType=6&displayZone=&zoneId=&pppStatus=0&agentName=,0,0,0,1,9068
            for line in ftp.readlines():
                myUrllist = line.split(',')
                for i in range(int(myUrllist[5]), int(myUrllist[6])):  # 每个list 存到 list中
                    url = myUrllist[0] + str(i) + myUrllist[1]
                    URL_inf = URLinformation(url, int(myUrllist[2]), 0.0, float(myUrllist[4]))  # 格式
                    URL_inf.Flag = 0
                    URL_inf.DeepNum = 1
                    URL_inf.domain = UrlUtil.getdomain(url)
                    MyUrl_SourceList.append(URL_inf)
        ftp.close()
        return MyUrl_SourceList

    @staticmethod
    def readSourceList():
        '''
        构造URL配置文件
        :return: URL LIST对象
        '''
        if USE_BXBLS is True:
            MyUrl_SourceList = []
            ftp = open(SOURCEURL_FILENAME, 'r')
            #http://www.ccgp.gov.cn/cggg/dfgg/index,0,0,0,0,24
            for line in ftp.readlines():
                myUrllist = line.split(',')
                for i in range(int(myUrllist[4]), int(myUrllist[5])+1):  # 每个list 存到 list中
                    if i ==0:
                        url = myUrllist[0] +".htm"
                    else:
                        url = myUrllist[0] +"_"+ str(i)+".htm"

                    URL_inf = URLinformation(url, int(myUrllist[1]), 0.0, float(myUrllist[2]))  # 格式
                    URL_inf.Flag = 0
                    URL_inf.DeepNum = 1
                    URL_inf.domain = UrlUtil.getdomain(url)
                    MyUrl_SourceList.append(URL_inf)

        else:
            MyUrl_SourceList = []
            ftp = open(SOURCEURL_FILENAME, 'r')
            # http://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index=,&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=1&dbselect=bidx&kw=&start_time=2013%3A04%3A09&end_time=2014%3A04%3A08&timeType=6&displayZone=&zoneId=&pppStatus=0&agentName=,0,0,0,1,9068
            for line in ftp.readlines():
                myUrllist = line.split(',')
                for i in range(int(myUrllist[5]), int(myUrllist[6])):  # 每个list 存到 list中
                    url = myUrllist[0] + str(i) + myUrllist[1]
                    URL_inf = URLinformation(url, int(myUrllist[2]), 0.0, float(myUrllist[4]))  # 格式
                    URL_inf.Flag = 0
                    URL_inf.DeepNum = 1
                    URL_inf.domain = UrlUtil.getdomain(url)
                    MyUrl_SourceList.append(URL_inf)
        ftp.close()
        return MyUrl_SourceList

        # urlInformationList = ConfigUtil.readTaskList()
        # for urlInfor in urlInformationList:
        #     data = urlInfor.class2dict()
        #     diststrjson = json.dumps(data)
        #     print(diststrjson)

    @staticmethod
    def readTaskList():
        MyUrl_SourceList = []
        ftp = open(TASK_FILENAME, 'r')
        for line in ftp.readlines():
            line = line.strip("\n")
            if not UrlUtil.isLegalUrl(line):
                break
            URL_inf = URLinformation(line, 0, 0.0, 0)  # 格式
            URL_inf.Flag = 0
            URL_inf.DeepNum = 1
            URL_inf.domain = UrlUtil.getdomain(line)
            MyUrl_SourceList.append(URL_inf)

        ftp.close()
        return MyUrl_SourceList

    @staticmethod
    def getItems(section):
        '''
        获取section下所有kv对
        :param section: section名
        :return:
        '''
        return __class__._getConfig()._sections[section]

    @staticmethod
    def get(section,option):
        '''
        获取section下option对应的值
        :param section: section名
        :param option: option名
        :return:object
        '''
        return __class__._getConfig().get(section,option)

    @staticmethod
    def getInt(section,option):
        '''
        获取section下option对应的int值
        :param section:
        :param option:
        :return:int
        '''
        return __class__._getConfig().getint(section,option)

    @staticmethod
    def getBoolean(section,option):
        '''
        获取section下option对应的boolean值
        :param section:
        :param option:
        :return:int
        '''
        return __class__._getConfig().getboolean(section,option)

    @staticmethod
    def getFloat(section, option):
        '''
        获取section下option对应的float值
        :param section:
        :param option:
        :return:int
        '''
        return __class__._getConfig().getfloat(section, option)

if __name__ == '__main__':

    urlInformationList = ConfigUtil.readSourceListRealTime()
    for urlInfor in urlInformationList:
        data = urlInfor.class2dict()
        diststrjson = json.dumps(data)
        print(diststrjson)
    # items=ConfigUtil.getItems('scheduler')
    # print (items)
