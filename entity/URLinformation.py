# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     URLinformation
   Description :
   Author :       ZWZ
   date：          18-5-10
-------------------------------------------------
   Change Activity:
                   18-5-10:
-------------------------------------------------
"""
__author__ = 'ZWZ'


class URLinformation():
    def __init__(self, Urlname=None, DeepNum=0, SleepTime=0.0, LastTime=0.0, Flag=0, State=0, Keyword=None, soup=None,
                 content=None, title=None, FilePath=None, FileName=None, Download=False, domain=None, fatherUrl=None, province=None):
        self.Urlname = Urlname  # url
        self.DeepNum = DeepNum  # 访问深度
        self.SleepTime = SleepTime  # 下面时长
        self.LastTime = LastTime  # 上次访问时间
        self.Flag = Flag  # domian标志
        self.State = State  # 区别bing与子链接
        self.Keyword = Keyword  # 关键字
        self.content = content  # BeautifulSoup前的一步
        self.soup = soup  # html内容
        self.title = title  # 标题
        self.FilePath = FilePath  # 文件路径,Example： "/home/wangyang/src/web_crawler/爬虫代码/"
        self.FileName = FileName  # 文件名
        self.Download = Download  # url类型标志，是否为下载文件
        self.domain = domain
        self.fatherUrl = fatherUrl
        self.province = province

    def setState(self, State):
        self.State = State

    def setSleepTime(self, SleepTime):
        self.SleepTime = SleepTime

    def setLastTime(self, LastTime):
        self.LastTime = LastTime

    def setKeyword(self, Keyword):
        self.Keyword = Keyword

    def class2dict(self):
        urlinformationdict = {"Urlname": self.Urlname,
                              "DeepNum": self.DeepNum,  # 访问深度
                              "SleepTime": self.SleepTime,  # 下面时长
                              "LastTime": self.LastTime,  # 上次访问时间
                              "Flag": self.Flag,  # domian标志
                              "State": self.State,  # 区别bing与子链接
                              "Keyword": self.Keyword,  # 关键字
                              "content": self.content,  # BeautifulSoup前的一步
                              "soup": self.soup,  # html内容
                              "title": self.title,  # 标题
                              "FilePath": self.FilePath,  # 文件路径,Example： "/home/wangyang/src/web_crawler/爬虫代码/"
                              "FileName": self.FileName,  # 文件名
                              "Download": self.Download,  # url类型标志，是否为下载文件
                              "domain": self.domain,
                              "fatherUrl": self.fatherUrl,
                              "province": self.province
                              }
        return urlinformationdict

    def dict2class(self, urlinformationdict):
        self.Urlname = urlinformationdict["Urlname"]  # url
        self.DeepNum = urlinformationdict["DeepNum"]  # 访问深度
        self.SleepTime = urlinformationdict["SleepTime"]  # 下面时长
        self.LastTime = urlinformationdict["LastTime"]  # 上次访问时间
        self.Flag = urlinformationdict["Flag"]  # domian标志
        self.State = urlinformationdict["State"]  # 区别bing与子链接
        self.Keyword = urlinformationdict["Keyword"]  # 关键字
        self.content = urlinformationdict["content"]  # BeautifulSoup前的一步
        self.soup = urlinformationdict["soup"]  # html内容
        self.title = urlinformationdict["title"]  # 标题
        self.FilePath = urlinformationdict["FilePath"]  # 文件路径,Example： "/home/wangyang/src/web_crawler/爬虫代码/"
        self.FileName = urlinformationdict["FileName"]  # 文件名
        self.Download = urlinformationdict["Download"]  # url类型标志，是否为下载文件
        self.domain = urlinformationdict["domain"]
        self.fatherUrl = urlinformationdict["fatherUrl"]
        self.province = urlinformationdict["province"]




