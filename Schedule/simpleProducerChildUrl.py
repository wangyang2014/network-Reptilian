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
import datetime
import hashlib
import json
import os
import random
import urllib
from lxml import etree
from os.path import basename
from urllib.parse import urlsplit, urlparse, urljoin

import requests
import sys

from bs4 import BeautifulSoup
from requests import Timeout
import re

from conf.Setting import USE_SOURCEURL_TYPE, USE_ASYNCTASK_TYPE, USE_PROXY, PROXY_NONE_URL, HEADERS, USE_BXBLS, Dbdata, \
    crawlerStartTime, crawlerEndTime, DbdataCCGPDFZB
from dbClient.Mongodb_Operator import Mongodb_Operator
from entity.URLinformation import URLinformation
from kafkaClient.kafkaUrlinformation import kafkaUrlinformation
from kafkaClient.localKafkaUrlinformation import localKafkaUrlinformation
from proxyClient.proxyClient import getIpProxyPool, getIpProxyPoolFromeRemote
from utils.ConfigUtil import ConfigUtil
from utils.HeadersEngine import HeadersEngine

__author__ = 'ZWZ'
from utils.LogUtil import Log
import time

class simpleProducerChildUrl():
    def __init__(self, processName, crontab):
        self.processName = processName
        self.crontab = crontab
        #Initial ipProxy and heads
        self.ipProxy = self.getIpPoolMethod()
        self.headersEngine = HeadersEngine()
        self.heads = self.headersEngine.getHeaders()
        #数据库模型和控制器
        self.URL_inf = URLinformation()
        self.__Sendcollection = "httpsearchccgpgovcn"
        self.mogodbControl = None

    def downLoadHtml(self, data):
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

                req = requests.get(data['Urlname'], headers=self.heads, allow_redirects=False, proxies=proxiesmmm, timeout=3)
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
                    data = self.__downlowdFile(data=data, req=req)
                    data['Download'] = 1
                elif "text" in reqheaders["Content-Type"]:
                    html = req.content
                    data['Download'] = 0
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
                if html is None:
                    Flag = 1
                # if count > 4:
                #     return None
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
            data['content'] = html
            soup = BeautifulSoup(html, 'html.parser')#很棒棒的bs简单解析下
        else:
            soup = None

        data['soup'] = soup
        # Log.i(data['content'].decode('utf-8'))
        return data

    def getChildrenLink(self,pageIndex):
        """
        获取子链接
        :return:
        """
        pattern = r'htt(p|ps):\/\/(\w+\.)+\w+/(\w+/)*'
        pattern = re.compile(pattern)
        # print("domain" + str(self.Url_inf.Urlname))
        Keyvalue = pattern.search(pageIndex['Urlname'])
        # Keyvalue  <_sre.SRE_Match object; span=(0, 26), match='http://search.ccgp.gov.cn/'>
        # print("Keyvalue  " + str(Keyvalue))
        # print(self.Url_inf.Urlname)
        if Keyvalue != None:
            Keyvalue = Keyvalue.group()
        else:
            Keyvalue = domain = urlparse(pageIndex['Urlname']).scheme + "://" + urlparse(pageIndex['Urlname']).netloc

        domain = Keyvalue
        URL_infor = []
        URL_infor2 = []
        Links = []
        link2 = ''
        title = ''
        currentTime = ''
        total_title = ''

        # if self.Url_inf.soup == None:
        #     return []
        if USE_BXBLS is True:
            #分成两个业务
            # if self.Url_inf.Urlname.find("zygg"):
            #     ul_content = self.Url_inf.soup.select(".c_list_bid")[0]
            # elif self.Url_inf.Urlname.find("dfgg"):
            #     ul_content = self.Url_inf.soup.select(".c_list_bid")[0]
            # else:
            #     ul_content = self.Url_inf.soup
            if pageIndex['soup'] is None:
                return []
            else:
                urlInfoList = pageIndex['soup'].select(".vT-srch-result-list-bid")

            if urlInfoList is None:
                return []

            if urlInfoList:
                ul_content = urlInfoList[0]
            else:
                return []

            for li in ul_content.select("li"):
                link = li.select("a")[0]

                # emProvince = li.select("span")[2].get_text()
                spanProvince = li.select("span")[0]
                emProvince = spanProvince.select("a")[0].get_text()
                currentTime = time.time()

                try:
                    href2 = link['href']
                    total_title = link['title']
                except KeyError:
                    pageIndex['soup'].select("a").remove(link)
                # else:
                if (href2.startswith("/")):  # startswith() 方法用于检查字符串是否是以指定子字符串开头，如果是则返回 True，否则返回 False
                    # link2 = urljoin(self.Url_inf.Urlname, href2)
                    # print(str(link2))

                    # link2=self.Url_inf.Urlname+href2
                    title = link.text.replace('\n', '').replace('\t', '').replace(' ', '')
                elif (href2.startswith("../../..")):
                    title = link.text.replace('\n', '').replace('\t', '').replace(' ', '')
                    # link2=href2.replace('../../..',domain)
                elif href2.startswith(".."):
                    title = link.text.replace('\n', '').replace('\t', '').replace(' ', '')
                    # link2=href2.replace('..',domain)
                elif href2.startswith("./"):
                    title = link.text.replace('\n', '').replace('\t', '').replace(' ', '')
                    # link2=href2.replace('./',domain+'/')
                elif 'http' in href2 and 'gov' in href2:
                    title = link.text.replace('\n', '').replace('\t', '').replace(' ', '')
                    # link2=href2

                link2 = urljoin(pageIndex['Urlname'], href2)
                # print("link2 is :" + str(link2))
                #title不全的问题
                if title.find("...") > -1:
                    title = total_title

                title = title.strip('\r')
                myLinkUrl = URLinformation(Urlname=link2, title=title, DeepNum=pageIndex['DeepNum'] - 1,
                                           domain=pageIndex['domain'], fatherUrl=pageIndex['Urlname'], province=emProvince, LastTime=currentTime)
                URL_infor.append(myLinkUrl)

        else:
            for link in pageIndex['soup'].select("a"):
                # print(str(self.Url_inf.soup))
                # <a href="http://www.ccgp.gov.cn/cggg/dfgg/gkzb/201310/t20131008_3148218.htm" style="line-height:18px" target="_blank">
                #                                         南方科技大学等离子体技术基础仪器采购项目招标公告
                #                                     </a>
                # <a href="http://www.ccgp.gov.cn/cggg/dfgg/gkzb/201309/t20130926_3144053.htm" style="line-height:18px" target="_blank">
                #                                         2013年国家良种补贴牦牛、绵羊、奶牛冻精、肉牛冻精采购项目公开招标公告
                # print("children url is : "+ str(link))
                try:
                    href2 = link['href']  # 取出href对应的网站信息 具体信息如上
                    # print("href2:   " + str(href2))
                    # 取出的信息包含情况如下3种
                    # http://www.ccgp.gov.cn/cggg/dfgg/gkzb/201309/t20130926_3144362.htm
                    # javascript:void(0)
                    # #
                except KeyError:
                    pageIndex['soup'].select("a").remove(link)

                else:  # try正确运行 则运行else
                    if (href2.startswith("/")):  # startswith() 方法用于检查字符串是否是以指定子字符串开头，如果是则返回 True，否则返回 False
                        # link2 = urljoin(self.Url_inf.Urlname, href2)
                        # print(str(link2))

                        # link2=self.Url_inf.Urlname+href2
                        title = link.text.replace('\n', '').replace('\t', '').replace(' ', '')
                    elif (href2.startswith("../../..")):
                        title = link.text.replace('\n', '').replace('\t', '').replace(' ', '')
                        # link2=href2.replace('../../..',domain)
                    elif href2.startswith(".."):
                        title = link.text.replace('\n', '').replace('\t', '').replace(' ', '')
                        # link2=href2.replace('..',domain)
                    elif href2.startswith("./"):
                        title = link.text.replace('\n', '').replace('\t', '').replace(' ', '')
                        # link2=href2.replace('./',domain+'/')
                    elif 'http' in href2 and 'gov' in href2:
                        title = link.text.replace('\n', '').replace('\t', '').replace(' ', '')
                        # link2=href2

                    link2 = urljoin(pageIndex['Urlname'], href2)
                    # print("link2 is :" + str(link2))
                    myLinkUrl = URLinformation(Urlname=link2, title=title, DeepNum=pageIndex['DeepNum'] - 1,
                                               domain=pageIndex['domain'], fatherUrl=pageIndex['Urlname'])
                    URL_infor.append(myLinkUrl)

        if USE_BXBLS is True:
            Links = list(set(URL_infor))
        else:
            #TODO 出现AttributeError: 'NoneType' object has no attribute 'select'
            for http in pageIndex['soup'].select('option'):  # 暂时未知有何内容
                try:
                    http2 = http['value']
                    # print("option" + str(http))
                except KeyError:
                    pageIndex['soup'].select("option").remove(http)
                else:
                    if "gov" in http2 and 'http' in http2:
                        myLinkUrl2 = URLinformation(Urlname=http2, title=http.text, DeepNum=pageIndex['DeepNum'] - 1,
                                                    domain=pageIndex['domain'], fatherUrl=pageIndex['Urlname'])
                        URL_infor2.append(myLinkUrl2)

            Links = list(set(URL_infor + URL_infor2))

        #TODO [2018-05-15 18:13:47.492] [INFO] [31469] [getChildrenLink(),ParseCCGPModule.py:129]: This url have 56  children urls1
        Log.i("This url have " + str(len(Links)) + "  children urls"+str(pageIndex['DeepNum']))
        return Links

    def getPageNumFromHome(self, dowloadData):
        """
        获取分页的页码URL
        """
        if dowloadData['soup'] is None:
            return []
        else:
            # Log.i(dowloadData['content'].decode('utf-8'))
            selector = etree.HTML(dowloadData['content'].decode('utf-8'))

            try:
                page = (int(selector.xpath('//div[@class="vT_z"]/div[1]/div/p[1]/span[2]/text()')[0]) // 20) + 3
            except:
                return []

            if page is None:
                return []
            parentURL_infor = []
            #随机数的方法判断倒序
            num = random.randint(3, 7)
            #存放url
            tempUrl = ''
            if (num % 2) == 0:
                for i in range(1, page):
                    #TODO字符串替换有问题
                    #'http://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index=1&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=0&dbselect=bidx&kw=&start_time=2018%3A06%3A04&end_time=2018%3A06%3A11&timeType=6&displayZone=&zoneId=&pppStatus=0&agentName='
                    # x = 'page_index=' + str(i)
                    # dowloadData['Urlname'] = re.sub(r'page_index=(.)', x, dowloadData['Urlname'])
                    #TODO 这里拼接数据有问题
                    # dowloadData['Urlname'] = 'http://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index=' + str(i) \
                    #                          + '&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=0&dbselect=bidx&kw=&start_time='\
                    #                          +crawlerStartTime+'&end_time='+crawlerEndTime+'&timeType=6&displayZone=&zoneId=&pppStatus=0&agentName='
                    x = 'page_index=' + str(i)
                    tempUrl = re.sub(r'page_index=(.)', x, dowloadData['Urlname'])
                    Log.i("parseUrl<<"+tempUrl)
                    urlChildInfo = URLinformation(Urlname=tempUrl, title=dowloadData['title'], DeepNum=dowloadData['DeepNum'],
                                                domain=dowloadData['domain'], fatherUrl=dowloadData['fatherUrl'])
                    parentURL_infor.append(urlChildInfo)
                else:
                    if parentURL_infor is not None:
                        page = 0
                        return parentURL_infor
            else:
                for i in range(page-1, 0, -1):
                    #TODO字符串替换有问题
                    #'http://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index=1&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=0&dbselect=bidx&kw=&start_time=2018%3A06%3A04&end_time=2018%3A06%3A11&timeType=6&displayZone=&zoneId=&pppStatus=0&agentName='
                    # x = 'page_index=' + str(i)
                    # dowloadData['Urlname'] = re.sub(r'page_index=(.)', x, dowloadData['Urlname'])
                    # dowloadData['Urlname'] = 'http://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index=' + str(i) \
                    #                          + '&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=0&dbselect=bidx&kw=&start_time='\
                    #                          +crawlerStartTime+'&end_time='+crawlerEndTime+'&timeType=6&displayZone=&zoneId=&pppStatus=0&agentName='

                    x = 'page_index=' + str(i)
                    tempUrl = re.sub(r'page_index=(.)', x, dowloadData['Urlname'])
                    Log.i("parseUrl<<"+tempUrl)
                    urlChildInfo = URLinformation(Urlname=tempUrl, title=dowloadData['title'], DeepNum=dowloadData['DeepNum'],
                                                domain=dowloadData['domain'], fatherUrl=dowloadData['fatherUrl'])
                    parentURL_infor.append(urlChildInfo)
                else:
                    if parentURL_infor is not None:
                        page = 0
                        return parentURL_infor

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

    def simpleRun(self):
        '''
        生产进程执行，每隔60*60*60*24秒，循环读取tasks
        :return:
        '''
        Log.i ('ProducerUrl.run() in {0}'.format(time.ctime()))
        while True:
            #资源检查
            # KafkaOperator = kafkaUrlinformation()
            KafkaOperator = localKafkaUrlinformation()
            # if self.mogodbControl is None:
            #     self.mogodbControl = Mongodb_Operator(Dbdata["host"], Dbdata["port"], Dbdata["db_name"],
            #                                       Dbdata["default_collection"])
            #解析数据源
            # if USE_SOURCEURL_TYPE is True:
            #     if USE_ASYNCTASK_TYPE is True:
            #         urlInformationList = ConfigUtil.readSourceListRealTime()
            #     else:
            #         urlInformationList = ConfigUtil.readSourceList()
            # else:
            #     urlInformationList = ConfigUtil.readTaskList()

            urlInformationList = ConfigUtil.readSourceListRealTime()

            #爬取,解析子URL
            if urlInformationList is None:
                continue

            for urlInfor in urlInformationList:
                data = urlInfor.class2dict()

                #获取首页内容
                dowloadData = self.downLoadHtml(data)
                if dowloadData is None:
                    continue
                # 解析提取分页url
                pageData = self.getPageNumFromHome(dowloadData)
                if pageData is None:
                    continue
                for pageIndex in pageData:
                    # 获取首页内容
                    dowloadPageData = self.downLoadHtml(pageIndex.class2dict())
                    if dowloadPageData is None:
                        continue
                    #提取子链接
                    # self.URL_inf.dict2class(pageIndex)
                    ccgpChildrenLink = self.getChildrenLink(dowloadPageData)
                    if ccgpChildrenLink is None:
                        continue
                    #KAFKA下发子链接
                    for link in ccgpChildrenLink:
                        # 检查Mongo
                        if self.mogodbControl is None:
                            self.mogodbControl = Mongodb_Operator(DbdataCCGPDFZB["host"], DbdataCCGPDFZB["port"], DbdataCCGPDFZB["db_name"], DbdataCCGPDFZB["default_collection"])
                        # 查重,不重复发送到kafka节省资源
                        if link.title is None:#标题为空的不发送
                            continue
                        uuid = self.get_md5(link.Urlname, link.title)
                        item = {"uuid": uuid}
                        value = self.mogodbControl.findone(item, self.__Sendcollection)  # 查询到返回文档
                        # #TODO 插入数据库有问题
                        if value is not None:#数据库查重
                            continue
                        # 于浩说不要发父链接给他
                        if link.DeepNum >= 0:
                            producerData = json.dumps(link.class2dict())
                            Log.i("produce<<" + producerData)
                            KafkaOperator.producerUrl(producerData)

            #日执行一次不用休眠了.使用crontab定时任务驱动
            if self.crontab==1:
                os._exit(0)
            else:
                # #休眠n秒(从配置文件中读取)
                items=ConfigUtil.getItems('producerScheduler')
                interval_min = items['interval_min']
                interval_max = items['interval_max']
                seconds=random.randint(int(interval_min),int(interval_max))
                Log.i('StartProducerUrl sleep ' + str(seconds) + ' seconds')
                time.sleep(seconds)

