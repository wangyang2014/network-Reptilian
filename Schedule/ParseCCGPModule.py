# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ParseCCGPModule
   Description : 解析CCGP子链接
   Author :       ZWZ
   date：          18-5-14
-------------------------------------------------
   Change Activity:
                   18-5-14:
-------------------------------------------------
"""
import hashlib
import json

import re
import urllib
from urllib.parse import urlparse, urljoin
from datetime import datetime

from callback import AsycThread
from conf.Setting import DbdataCCGPDFZB, USE_BXBLS, USE_SOURCEURL_TYPE
from dbClient.Mongodb_Operator import Mongodb_Operator
from entity.URLinformation import URLinformation
from utils.LogUtil import Log

__author__ = 'ZWZ'

class ParserCCGPModule():
    def __init__(self, Url_inf, KafkaOperator):
        self.myDb = Mongodb_Operator(DbdataCCGPDFZB["host"], DbdataCCGPDFZB["port"], DbdataCCGPDFZB["db_name"], DbdataCCGPDFZB["default_collection"])
        self.Url_inf = Url_inf
        self.KafkaOperator = KafkaOperator

    def get_md5(self):

        #如果content为none，只编码url
        """
        用MD5编码内容生成
        :return:
        """
        # if self.Url_inf.title != None:
        #     return hashlib.md5((self.Url_inf.Urlname+self.Url_inf.title).encode("utf-8")).hexdigest()#使用md5编码
        # else:
        #     return hashlib.md5((self.Url_inf.Urlname).encode("utf-8")).hexdigest()#使用md5编码

        # if self.Url_inf.content is not  None and self.Url_inf.Urlname is not None and self.Url_inf.title is not None:
        #     return hashlib.md5((urllib.parse.unquote(self.Url_inf.Urlname).join(str(self.Url_inf.content)).encode("utf-8"))).hexdigest()  # 使用md5编码
        #     # return hashlib.md5((self.Url_inf.Urlname+self.Url_inf.title.decode("utf8","ignore")).encode("utf-8")).hexdigest()#使用md5编码
        # else:
        #     return hashlib.md5((urllib.parse.unquote(self.Url_inf.Urlname).join(str(self.Url_inf.content)).encode(
        #         "utf-8"))).hexdigest()  # 使用md5编码
        return hashlib.md5((urllib.parse.unquote(self.Url_inf.Urlname).join(str(self.Url_inf.content)).encode(
            "utf-8"))).hexdigest()  # 使用md5编码

    # @AsycThread.async
    def getChildrenLink(self):
        """
        获取子链接
        :return:
        """
        pattern = r'htt(p|ps):\/\/(\w+\.)+\w+/(\w+/)*'
        pattern = re.compile(pattern)
        # print("domain" + str(self.Url_inf.Urlname))
        Keyvalue = pattern.search(self.Url_inf.Urlname)
        # Keyvalue  <_sre.SRE_Match object; span=(0, 26), match='http://search.ccgp.gov.cn/'>
        # print("Keyvalue  " + str(Keyvalue))
        # print(self.Url_inf.Urlname)
        if Keyvalue != None:
            Keyvalue = Keyvalue.group()
        else:
            Keyvalue = domain = urlparse(self.Url_inf.Urlname).scheme + "://" + urlparse(self.Url_inf.Urlname).netloc

        domain = Keyvalue
        URL_infor = []
        URL_infor2 = []
        Links = []
        link2 = ''
        title = ''
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
            if self.Url_inf.soup is None:
                return []
            else:
                urlInfoList = self.Url_inf.soup.select(".c_list_bid")

            if urlInfoList is None:
                return []

            if urlInfoList:
                ul_content = urlInfoList[0]
            else:
                return []

            for li in ul_content.select("li"):
                link = li.select("a")[0]
                emProvince = li.select("em")[2].get_text()

                try:
                    href2 = link['href']
                    total_title = link['title']
                except KeyError:
                    self.Url_inf.soup.select("a").remove(link)
                else:
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

                    link2 = urljoin(self.Url_inf.Urlname, href2)
                    # print("link2 is :" + str(link2))
                    #title不全的问题
                    if title.find("...") > -1:
                        title = total_title

                    myLinkUrl = URLinformation(Urlname=link2, title=title, DeepNum=self.Url_inf.DeepNum - 1,
                                               domain=self.Url_inf.domain, fatherUrl=self.Url_inf.Urlname, province=emProvince)
                    URL_infor.append(myLinkUrl)

        else:
            for link in self.Url_inf.soup.select("a"):
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
                    self.Url_inf.soup.select("a").remove(link)

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

                    link2 = urljoin(self.Url_inf.Urlname, href2)
                    # print("link2 is :" + str(link2))
                    myLinkUrl = URLinformation(Urlname=link2, title=title, DeepNum=self.Url_inf.DeepNum - 1,
                                               domain=self.Url_inf.domain, fatherUrl=self.Url_inf.Urlname)
                    URL_infor.append(myLinkUrl)

        if USE_BXBLS is True:
            Links = list(set(URL_infor))
        else:
            #TODO 出现AttributeError: 'NoneType' object has no attribute 'select'
            for http in self.Url_inf.soup.select('option'):  # 暂时未知有何内容
                try:
                    http2 = http['value']
                    # print("option" + str(http))
                except KeyError:
                    self.Url_inf.soup.select("option").remove(http)
                else:
                    if "gov" in http2 and 'http' in http2:
                        myLinkUrl2 = URLinformation(Urlname=http2, title=http.text, DeepNum=self.DeepNum - 1,
                                                    domain=self.Url_inf.domain, fatherUrl=self.Url_inf.Urlname)
                        URL_infor2.append(myLinkUrl2)

            Links = list(set(URL_infor + URL_infor2))

        #TODO [2018-05-15 18:13:47.492] [INFO] [31469] [getChildrenLink(),ParseCCGPModule.py:129]: This url have 56  children urls1
        Log.i("This url have " + str(len(Links)) + "  children urls"+str(self.Url_inf.DeepNum))
        return Links

    @AsycThread.async
    def savedata(self):
        """
        保存数据到mongodb
        """
        uuid = self.get_md5()
        item = {"uuid": uuid, "url": self.Url_inf.Urlname, "title": self.Url_inf.title,
                "time": datetime.now().timestamp(),
                "lastTime": self.Url_inf.LastTime,
                "content": self.Url_inf.content, "fatherUrl": self.Url_inf.fatherUrl, "province":self.Url_inf.province}
        string = self.Url_inf.domain.replace('.', '').replace('/', '').replace(':', '')
        # 查重 删除 替换
        if USE_SOURCEURL_TYPE is True:
            if self.Url_inf.province is not None and self.Url_inf.content is not None:
                value = self.myDb.findone({"uuid": uuid})  # 查询到返回文档
                if value is None:
                    Log.i(self.Url_inf.content.decode('utf-8'))
                    self.myDb.insert(item, string)
                    self.myDb.ensure_index("uuid", string)
                    self.KafkaOperator.producterUUID(json.dumps({"uuid": uuid, 'collection': string}))
        else:
            self.myDb.insert(item, string)
            self.myDb.ensure_index("uuid", string)
            self.KafkaOperator.producterUUID(json.dumps({"uuid": uuid, 'collection': string}))

    def getLinks(self):
        """
        对外接口获取子链接
        :return:
        """
        if self.Url_inf.Download :
            return []
        else:
            #异步存储
            self.savedata()
            return self.getChildrenLink()

    def setURL_inf(self, URL_inf):
        """
        接口
        :param URL_inf:
        """
        self.Url_inf = URL_inf

    # def __del__(self):
    #     """
    #     关闭数据库连接
    #     """
    #     self.myDb.close_conn()

