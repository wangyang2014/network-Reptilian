# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyIpPool
   Description : URL下载任务器
   Author :       ZWZ
   date：          18-5-13
-------------------------------------------------
   Change Activity:
                   18-5-13:
-------------------------------------------------
"""
import hashlib
import json
import urllib
import random
from multiprocessing import Pipe
from multiprocessing import Process
from os.path import basename
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup
from multiprocessing import Manager
from requests import Timeout

from Schedule.ParseCCGPModule import ParserCCGPModule
from callback import AsycThread
from conf.Setting import PROXY_NONE_URL, USE_PROXY, Dbdata, HEADERS
from dbClient.Mongodb_Operator import Mongodb_Operator
from entity.URLinformation import URLinformation
from kafkaClient.kafkaUrlinformation import kafkaUrlinformation
from proxyClient.proxyClient import getIpProxyPool, getIpProxyPoolFromeRemote
from utils.ConfigUtil import ConfigUtil
from utils.HeadersEngine import HeadersEngine

from utils.LogUtil import Log
import multiprocessing
import time

import threading
mutex_lock = threading.RLock()  # 互斥锁的声明

__author__ = 'ZWZ'


class Downloader(multiprocessing.Process):
    def __init__(self, processName, pipeDictData):
        multiprocessing.Process.__init__(self)
        self.processName = processName
        self.pipeDictData = pipeDictData#任务url消息队列

        #数据库模型和控制器
        self.__Sendcollection = "Send_collection"
        self.URL_inf = URLinformation()
        # self.mogodbControl = Mongodb_Operator(Dbdata["host"], Dbdata["port"], Dbdata["db_name"], Dbdata["default_collection"])
        #这里还是设计成单个进程使用Mongo,不然TM给我警告
        self.mogodbControl = None

    def ayncDownloadTask(self, ipProxy,DictData):
        """
        异步执行爬虫业务
        :param ipProxy:
        :param DictData:
        :return:
        """
        # Log.i(DictData)
        global mutex_lock
        mutex_lock.acquire()  # 临界区开始，互斥的开始

        if self.URL_inf is None:
            self.URL_inf = URLinformation()

        # 源数据处理(实体类)
        self.URL_inf.dict2class(DictData)
        # # 查重业务逻辑
        # if self.__checkURL(self.URL_inf.Urlname):
        #     return
        # else:
        #     item = {"_id": self.__getMD5(self.URL_inf.Urlname)}
        #     self.mogodbControl.insert(item, self.__Sendcollection)

        # TODO 这里沿用王洋以前代码逻辑
        self.URL_inf = self.__getSoupAndDeepnumOrDown(ipProxy)
        if self.URL_inf is None or self.URL_inf.Urlname is None or self.URL_inf.content is None:
            mutex_lock.release()  # 临界区结束，互斥的结束
            return

        # 查重业务逻辑,uid=urlName+content
        # hashlib.md5((self.Url_inf.Urlname + self.Url_inf.content.decode("utf8", "ignore")).encode(
        #     "utf-8")).hexdigest()  # 使用md5编码
        #抛出AttributeError: 'NoneType' object has no attribute 'decode'异常
        # checkUrlUID = self.URL_inf.Urlname+self.URL_inf.title.decode("utf8","ignore")
        # checkUrlUID = urllib.parse.unquote(self.URL_inf.Urlname)
        # checkUrlUID = checkUrlUID.join(str(self.URL_inf.content))

        # checkUrlUID = hashlib.md5((urllib.parse.unquote(self.URL_inf.Urlname).join(str(self.URL_inf.content)).encode(
        #     "utf-8"))).hexdigest()  # 使用md5编码
        #
        # if self.__checkURL(checkUrlUID):
        #     mutex_lock.release()  # 临界区结束，互斥的结束
        #     return
        # else:
        #     item = {"_id": self.__getMD5(checkUrlUID)}
        #     self.mogodbControl.insert(item, self.__Sendcollection)

        #发送子链接
        self._sendChildUrl(self.URL_inf, mutex_lock)

        mutex_lock.release()  # 临界区结束，互斥的结束

    @AsycThread.async
    def _sendChildUrl(self,URL_inf, mutex_lock):
        # # 保存数据并提取子链接重新投入生产对应的话题
        KafkaOperator = kafkaUrlinformation()
        # TODO 这里用类管理不同网站的逻辑
        parseCCGPModule = ParserCCGPModule(URL_inf, KafkaOperator)
        ccgpChildrenLink = parseCCGPModule.getLinks()

        if ccgpChildrenLink is None:
            mutex_lock.release()  # 临界区结束，互斥的结束
            return

        for link in ccgpChildrenLink:
            #于浩说不要发父链接给他
            if link.DeepNum >= 0:
                Log.i("produce<<"+json.dumps(link.class2dict()))
                KafkaOperator.producerUrl(json.dumps(link.class2dict()))

    def __downlowdFile(self, url, req):
        # http://stackoverflow.com/questions/862173/how-to-download-a-file-using-python-in-a-smarter-way
        """
        下载文件的代码逻辑.沿用王洋逻辑,还没调试
        :param url:
        :param req:
        """
        reqheaders = req.headers
        revealfn = url.split('/')[-1]

        if "." in revealfn[-6:]:
            fileName = revealfn
        else:
            if ('Content-Disposition' in reqheaders.keys()):
                fileName = reqheaders['Content-Disposition'].split('filename=')[1]
                fileName = fileName.replace('"', '').replace("'", "")
            else:
                r = urllib.request.urlopen(url)
                if r.url != url:
                    fileName = basename(urlsplit(r.url)[2])
            self.URL_inf.FileName = fileName

        _FileName = None
        if (self.URL_inf.FilePath):
            _FileName = str(self.URL_inf.FilePath) + fileName
        else:
            _FileName = fileName

        with open(_FileName, "wb") as donefile:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    donefile.write(chunk)

        Log.i("File:"+_FileName+"downLoaded")

    def __getSoupAndDeepnumOrDown(self, ipProxy, headers = []):
        """
        爬虫并简单解析子链接
        :param proxiesmmm:
        :param headers:
        """

        html = None#爬取网页所有内容
        ctifety = 0#解析子链接标志位
        Flag = 1#爬取完成标志位
        count = 0#空网页计算器

        #初始化你的头
        headers = HEADERS
        headersEngine = HeadersEngine()

        #奶奶的个大循环下载内容和文件,很JB耗时i/o操作
        while (Flag):
            url = self.URL_inf.Urlname#中间变量
            try:
                #如果有异常了赶紧换ip
                if count > 0:
                    ipProxy=self.getIpPoolMethod()
                protocol = 'https' if 'https' in ipProxy else 'http'
                proxiesmmm = {protocol: ipProxy}
                #Request Http请求网页,虽然我不喜欢这个库
                # req = requests.get(url, headers=headers, proxies=proxiesmmm, timeout=2)  # ,proxies=proxiesmmm,stream=True
                # req = requests.get(url, headers=headers, proxies=proxiesmmm)
                #解决HTTP超时异常 https://www.zhihu.com/question/52595659 拒绝默认的301/302重定向
                req = requests.get(url, headers=headers, allow_redirects=False, proxies=proxiesmmm, timeout=3)

                if req.status_code != 200:
                    return None

                reqheaders = req.headers
                if "application" in reqheaders["Content-Type"]:
                    self.__downlowdFile(url=url, req=req)
                    self.URL_inf.Download = 1
                elif "text" in reqheaders["Content-Type"]:
                    html = req.content
                    self.URL_inf.Download = 0
                    ctifety = 1
                    Flag = 0#该回大部队了
                else:
                    return None
            except requests.exceptions.ConnectTimeout as e:
                Log.e("getSoupAndDeepnumOrDown HeadError -> " + str(e))
                if count > 3:
                    return None
                pass
            except (ConnectionError, Timeout) as e:
                Flag = 1
                count+=1
                Log.e("getSoupAndDeepnumOrDown HeadError -> " + str(e))
                headers = headersEngine.getHeaders()
                #关闭多余的连接,出现了异常requests“Max retries exceeded with url” error
                s = requests.session()
                s.keep_alive = False
                if count > 3:
                    return None
                pass
            except Exception as e:
                Flag = 1
                count += 1
                #TODO 处理这种javascript:void(0)异常,忽略这种异常:https://www.zhihu.com/question/20626694?from=profile_question_card
                #TODO 处理这种无效头部异常 Invalid return character or leading space in header: Accept-Language
                #TODO 处理这种httpconnectionpool max retries  Failed to establish a new connection:
                Log.e("getSoupAndDeepnumOrDown Exception -> " + str(e))
                headers = headersEngine.getHeaders()
                #异常Max retries exceeded with url Error的处理
                s = requests.session()
                s.keep_alive = False
                if count > 3:
                    return None
                pass


        if ctifety:
            self.URL_inf.content = html
            soup = BeautifulSoup(html, 'html.parser')#很棒棒的bs简单解析下
        else:
            soup = None

        self.URL_inf.soup = soup
        # Log.i(self.URL_inf.content.decode('utf-8'))
        return self.URL_inf#终于TM的爬完和简单解析了

    def __getMD5(self, url):
        """
        如果content为none，只编码url
        :return:
        """
        return hashlib.md5(url.encode("utf-8")).hexdigest()  # 使用md5编码

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

    def run_downloader(self, pipeDictData):
        """
        下载驱动器
        :param queueDictData:数据源(队列)
        """
        #改成一个ip下载同一个网站机制
        ipProxy = None
        while True:
            # Log.i('run_downloader in {0}'.format(time.ctime()))
            #获取数据源
            DictData = pipeDictData.recv()

            # 数据来了再创建数据库链接
            if self.mogodbControl is None:
                self.mogodbControl = Mongodb_Operator(Dbdata["host"], Dbdata["port"], Dbdata["db_name"], Dbdata["default_collection"])
            #数据来了再去获取ip
            if DictData is not None:
                # 获取免费ip
                if ipProxy is None:
                    ipProxy = self.getIpPoolMethod()
                # 异步执行下载
                self.ayncDownloadTask(ipProxy, DictData)
            # else:
            #     # 休眠n秒(从配置文件中读取)
            #     items = ConfigUtil.getItems('consumerScheduler')
            #     interval_min = items['interval_min']
            #     interval_max = items['interval_max']
            #     seconds = random.randint(int(interval_min), int(interval_max))
            #     Log.i('run_downloader sleep ' + str(seconds) + ' seconds')
            #     time.sleep(seconds)
            #     continue

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
        # ipProxy = None
        # if ipProxy is None:
        #     if USE_PROXY is True:
        #         #获取代理的时候保证能至少有一个IP
        #         proxyIpPool = getIpProxyPool()
        #         proxyIpPoolFromeRemote = getIpProxyPoolFromeRemote()
        #
        #         if proxyIpPool is None:
        #             ipProxy = proxyIpPoolFromeRemote
        #         else:
        #             ipProxy = proxyIpPool
        #
        #         if ipProxy is None:
        #             ipProxy = PROXY_NONE_URL
        #     else:
        #         ipProxy = PROXY_NONE_URL
        #
        # return ipProxy


    def run(self):
        '''
        获取免费IP代理进程执行，循环读取tasks
        :return:
        '''
        Log.i('Downloader.run() in {0}'.format(time.ctime()))

        p_list = list()

        downloaderRun = Process(target=self.run_downloader, args=(self.pipeDictData,))
        p_list.append(downloaderRun)

        for p in p_list:
            p.daemon = True
            p.start()
        for p in p_list:
            p.join()

    # def __del__(self):
    #     '''
    #     析构方法
    #     :return: 无
    #     '''
    #     if self.mogodbControl is not None:
    #         self.mogodbControl.close_conn()
