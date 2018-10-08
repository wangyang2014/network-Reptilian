# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ProducerChildUrl
   Description : 批量生产子链接,含有下载解析部分的功能的生产者进程
   Author :       ZWZ
   date：          18-5-10
-------------------------------------------------
   Change Activity:
                   18-5-10:
-------------------------------------------------
"""
import hashlib
import json
import os
import random
import urllib
from datetime import datetime
import time

from lxml import etree
from os.path import basename
from urllib.parse import urlsplit, urlparse, urljoin

import requests
import sys

from bs4 import BeautifulSoup
from requests import Timeout
import re

from callback import AsycThread
from conf.Setting import USE_SOURCEURL_TYPE, USE_ASYNCTASK_TYPE, USE_PROXY, PROXY_NONE_URL, HEADERS, USE_BXBLS, Dbdata, \
    DbdataCCGPDFZB
from dbClient.Mongodb_Operator import Mongodb_Operator
from entity.URLinformation import URLinformation
from kafkaClient.localKafkaUrlinformation import localKafkaUrlinformation
from proxyClient.proxyClient import getIpProxyPool
from utils.ConfigUtil import ConfigUtil
from utils.HeadersEngine import HeadersEngine

__author__ = 'ZWZ'
from utils.LogUtil import Log
import multiprocessing

class ComsumerChildUrl(multiprocessing.Process):
    def __init__(self, processName, pipeDictData):
        multiprocessing.Process.__init__(self)
        self.processName = processName
        #Initial ipProxy and heads
        self.ipProxy = self.getIpPoolMethod()
        self.headersEngine = HeadersEngine()
        self.heads = self.headersEngine.getHeaders()
        #数据库模型和控制器
        self.URL_inf = URLinformation()
        self.__Sendcollection = "httpsearchccgpgovcn"
        self.mogodbControl = None
        self.KafkaOperator = None
        self.pipeDictData = pipeDictData  # 任务url消息队列

    def downLoadHtml(self):
        """
        爬取并提取子链接
        :param urlInfor:
        """
        if self.ipProxy is None:
            self.ipProxy = self.getIpPoolMethod()
        if self.heads is None:
            self.heads = self.headersEngine.getHeaders()

        # {'DeepNum': 1, 'fatherUrl': None, 'Download': False, 'province': None, 'domain': 'http://search.ccgp.gov.cn',
        #  'FileName': None, 'Keyword': None, 'title': None, 'LastTime': 0.0, 'Flag': 0, 'soup': None, 'State': 0,
        #  'content': None,
        #  'Urlname': 'http://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index=1&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=1&dbselect=bidx&kw=&start_time=2018%3A06%3A07&end_time=2018%3A06%3A07&timeType=6&displayZone=&zoneId=&pppStatus=0&agentName=',
        #  'SleepTime': 0.0, 'FilePath': None}

        html = None#爬取网页所有内容
        ctifety = 0#解析子链接标志位
        Flag = 1#爬取完成标志位
        count = 0#空网页计算器
        while (Flag):
            try:
                if count > 1:
                    self.ipProxy = self.getIpPoolMethod()

                protocol = 'https' if 'https' in self.ipProxy else 'http'
                proxiesmmm = {protocol: self.ipProxy}

                req = requests.get(self.URL_inf.Urlname, headers=self.heads, allow_redirects=False, proxies=proxiesmmm, timeout=3)
                # 跳过验证反扒机制
                soup_validate = BeautifulSoup(req.text, 'lxml')
                if soup_validate.find(name='title').string == '安全验证':
                    self.ipProxy = self.getIpPoolMethod()
                    continue
                if req.status_code != 200:
                    self.ipProxy = self.getIpPoolMethod()
                    continue

                reqheaders = req.headers
                if "application" in reqheaders["Content-Type"]:
                    data = self.__downlowdFile(data=self.URL_inf, req=req)
                    data['Download'] = 1
                elif "text" in reqheaders["Content-Type"]:
                    html = req.content
                    self.URL_inf.Download = 0
                    ctifety = 1
                    Flag = 0  # 该回大部队了
                else:
                    continue
            except requests.exceptions.ConnectTimeout as e:
                Log.e("getSoupAndDeepnumOrDown HeadError -> " + str(e))
                self.heads = self.headersEngine.getHeaders()
                count += 1
                if html is None:
                    Flag = 1
            except (ConnectionError, Timeout) as e:
                Flag = 1
                count+=1
                Log.e("getSoupAndDeepnumOrDown HeadError -> " + str(e))
                self.heads = self.headersEngine.getHeaders()
                #关闭多余的连接,出现了异常requests“Max retries exceeded with url” error
                requests.adapters.DEFAULT_RETRIES = 5
                s = requests.session()
                s.keep_alive = False
                count += 1
                if html is None:
                    Flag = 1
                pass
            except Exception as e:
                Flag = 1
                count += 1
                #TODO 处理这种javascript:void(0)异常,忽略这种异常:https://www.zhihu.com/question/20626694?from=profile_question_card
                #TODO 处理这种无效头部异常 Invalid return character or leading space in header: Accept-Language
                #TODO 处理这种httpconnectionpool max retries  Failed to establish a new connection:
                Log.e("getSoupAndDeepnumOrDown Exception -> " + str(e))
                self.heads = self.headersEngine.getHeaders()
                #异常Max retries exceeded with url Error的处理
                s = requests.session()
                s.keep_alive = False
                count += 1
                if html is None:
                    Flag = 1
                pass

        if ctifety:
            self.URL_inf.content = html
            soup = BeautifulSoup(html, 'html.parser')#很棒棒的bs简单解析下
        else:
            soup = None

        self.URL_inf.soup = soup
        Log.i(self.URL_inf.content.decode('utf-8'))
        return self.URL_inf

    def __downlowdFile(self, data, req):
        # http://stackoverflow.com/questions/862173/how-to-download-a-file-using-python-in-a-smarter-way
        """
        下载文件的代码逻辑.沿用王洋逻辑,还没调试
        :param url:
        :param req:
        """
        reqheaders = req.headers
        revealfn = data['Urlname'].split('/')[-1]

        if "." in revealfn[-6:]:
            fileName = revealfn
        else:
            if ('Content-Disposition' in reqheaders.keys()):
                fileName = reqheaders['Content-Disposition'].split('filename=')[1]
                fileName = fileName.replace('"', '').replace("'", "")
            else:
                r = urllib.request.urlopen(data['Urlname'])
                if r.url != data['Urlname']:
                    fileName = basename(urlsplit(r.url)[2])
            data['FileName'] = fileName

        _FileName = None
        if (data['FilePath']):
            _FileName = str(data['FilePath']) + fileName
        else:
            _FileName = fileName

        with open(_FileName, "wb") as donefile:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    donefile.write(chunk)

        Log.i("File:"+_FileName+"downLoaded")
        return data

    def get_md5(self, url, content):

        #如果content为none，只编码url
        """
        用MD5编码内容生成
        :return:
        """
        return hashlib.md5((urllib.parse.unquote(url).join(str(content)).encode("utf-8"))).hexdigest()  # 使用md5编码

    def __checkURL(self, urlName):
        """
        查重函数
        :param urlName:
        :return:
        """
        item = {"_id": urlName}
        value = self.mogodbControl.findone(item, self.__Sendcollection)  # 查询到返回文档
        if value == None:  # 说明没找到
            return False
        else:
            return True  # 说明找到了

    def getIpPoolMethod(self):
        """
        获取免费代理ip
        :return: 返回一个免费的ip代理
        """
        ipProxy = None
        if ipProxy is None:
            if USE_PROXY is True:
                #获取代理的时候保证能至少有一个IP
                proxyIpPool = getIpProxyPool()
                if proxyIpPool is not None:
                    ipProxy = proxyIpPool

                if ipProxy is None:
                    ipProxy = PROXY_NONE_URL
            else:
                ipProxy = PROXY_NONE_URL

        return ipProxy

    # @AsycThread.async
    def savedata(self, data):
        """
        保存数据到mongodb
        """
        #查重
        uuid = self.get_md5(data.Urlname, data.title)
        urlInfo = {
            "uuid": uuid,
            "url": data.Urlname,
            "title": data.title,
            "time": datetime.now().timestamp(),
            "content": data.content,
            "fatherUrl": data.fatherUrl,
            "province": data.province,
            "LastTime": data.LastTime
        }
        string = data.domain.replace('.', '').replace('/', '').replace(':', '')
        #查重 删除 替换
        if data.province is not None and data.content is not None:
            item = {"uuid": uuid}
            value = self.mogodbControl.findone(item, self.__Sendcollection)  # 查询到返回文档
            #TODO 插入数据库有问题
            if value is None:
                # item = {"_id": uuid}
                self.mogodbControl.insert(urlInfo, self.__Sendcollection)
                # self.mogodbControl.ensure_index(item, self.__Sendcollection)
                self.KafkaOperator.producterUUID(json.dumps({"uuid": uuid, 'collection': string}))

    def run(self):
        '''
        生产进程执行，每隔60*60*60*24秒，循环读取tasks
        :return:
        '''
        Log.i ('ProducerUrl.run() in {0}'.format(time.ctime()))
        while True:
            #监听数据
            DictData = self.pipeDictData.recv()
            if DictData is None:
                continue
            #源数据处理(实体类)
            self.URL_inf.dict2class(DictData)
            #检查Mongo
            if self.mogodbControl is None:
                self.mogodbControl = Mongodb_Operator(DbdataCCGPDFZB["host"], DbdataCCGPDFZB["port"], DbdataCCGPDFZB["db_name"], DbdataCCGPDFZB["default_collection"])
            #检查Kafka
            if self.KafkaOperator is None:
                self.KafkaOperator = localKafkaUrlinformation()
            #查重
            uuid = self.get_md5(self.URL_inf.Urlname, self.URL_inf.title)
            item = {"uuid": uuid}
            value = self.mogodbControl.findone(item, self.__Sendcollection)  # 查询到返回文档
            # #TODO 插入数据库有问题
            if value is not None:
                continue
            #获取首页内容
            self.URL_inf = self.downLoadHtml()
            if self.URL_inf is None:
                continue
            #异步保存数据
            self.savedata(self.URL_inf)

            # #休眠n秒(从配置文件中读取)
            items=ConfigUtil.getItems('consumerScheduler')
            interval_min = items['interval_min']
            interval_max = items['interval_max']
            seconds=random.randint(int(interval_min),int(interval_max))
            Log.i('StartProducerUrl sleep ' + str(seconds) + ' seconds')
            time.sleep(seconds)

