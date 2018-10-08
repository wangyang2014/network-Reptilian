# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     Setting
   Description : 运行时不变配置
   Author :       ZWZ
   date：          18-5-9
-------------------------------------------------
   Change Activity:
                   18-5-9:
-------------------------------------------------
"""
import datetime

__author__ = 'ZWZ'

import configparser
import os
import click
from utils.TimeUtil import TimeUtil

##############
# Mongodb配置（数据落盘）
##############
#HQ数据库
Dbdata = {"host": '10.0.0.32',
          "port": 27017,
          "db_name": "HQ",
          "default_collection": "collection",
          "Link_collection": "Link_collection",
          "state_collection": "state_collection"
          }
#CCGPDFZB数据库
DbdataCCGPDFZB = {"host" : '10.0.0.32',
          "port" : 27017,
          "db_name" : "ccgp_daily_added",
          "default_collection" : "httpsearchccgpgovcn",
}

##############
# 日志數據庫系统（生产环境使用mongodb记录，开发请使用文件LOG)
##############
#Mongo主机和端口
MONGO_HOST = '10.0.0.32'
MONGO_PORT = 27017
#Mongo数据库名
MONGO_DB = 'log_test'
#访问Mongo的MONGO_DB数据库的MECHANISM认证。None：无认证，MONGODB-CR：2.x认证，SCRAM-SHA-1：3.x认证
MONGO_MECHANISM =None
#访问Mongo的MONGO_DB数据库的用户名和密码
MONGO_USER = ''
MONGO_PASSWORD = ''

##############
# 日志文件系统（生产环境使用mongodb记录，开发请使用文件LOG)
##############
# 工程根目录，注意此处以初次调用这个变量的元素为准，工程起始目录定位在main，若有修改请注意这个位置
BASE_PATH = os.path.split(os.path.split(__file__)[0])[0]
# 输出目录
OUTPUT_PATH = os.path.join(BASE_PATH, 'log')
# 输出分组，默认按年月日_时分秒分组
# OUTPUT_GROUP_PATH = os.path.join(OUTPUT_PATH, TimeUtil.getFormatTime('%Y%m%d_%H%M%S'))20180510_135742
LOG_FILENAME = os.path.join(OUTPUT_PATH, "webCrawler.log")
URL_INFO_FILENAME = os.path.join(OUTPUT_PATH, "urlInfor.log")
HEAD_INFO_FILENAME = os.path.join(OUTPUT_PATH, "headInfor.log")
#保存原來付費的ip池
COF_PATH = os.path.join(BASE_PATH, 'conf')
PROXIES_FILENAME = os.path.join(COF_PATH, 'proxies.ini')
#KfKa签名证书
CACERT_FILENAME = os.path.join(COF_PATH, 'ca-cert')
#TASK文件路径
TASK_FILENAME = os.path.join(COF_PATH, 'task.json')
#原URL构造文件路径
SOURCEURL_FILENAME = os.path.join(COF_PATH, 'myUrlSourcel.txt')
#true代表使用针对性网站如CCGP,FALSE代表通用网站
USE_SOURCEURL_TYPE = True
#异步发布生产者的任务
USE_ASYNCTASK_TYPE = True
#true代表爬取地方公告
USE_BXBLS = True
#http://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index=,&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=0&dbselect=bidx&kw=&start_time=2017%3A05%3A26&end_time=2018%3A05%3A03&timeType=6&displayZone=&zoneId=&pppStatus=0&agentName=,0,0,0,1,9068
#设置程序并发数
MAXTHREAD = 1000

##############
# KafKa配置
##############
kafka_setting = {
    'sasl_plain_username': 'LTAIOSohR36Hyjmu',
    'sasl_plain_password': 'WDO3jGgsgv',
    # 'bootstrap_servers': ["kafka-cn-internet.aliyun.com:8080"],
    'bootstrap_servers': ["kafka-cn-internet.aliyun.com:8080"],
    'topic_name': 'alikafka-ailongma_url_realtime',
    'topic_name_ccgp': 'alikafka-ailongma_parse_ccgp_realtime',
    'consumer_id': 'CID_alikafka_ailongma_G1'
}

##############
# KafKa本地配置
##############
localKafka_setting = {
    'bootstrap_servers': ["10.0.0.32:9092"],
    'topic_name': 'ailongma_url_realtime',
    'topic_name_ccgp': 'ailongma_parse_ccgp_realtime',
    'consumer_id': 'CID_alikafka_ailongma_G1'
}
##############
# 代理配置
##############
# 是否使用代理
USE_PROXY = True
# 代理请求url，若USE_PROXY为False则忽略此项,这里可以使用分布式抓取免费代理
PROXY_URL = 'http://127.0.0.1:5010/get'
PROXY_REMOTE_URL = 'http://123.207.35.36:5010/get'
#没有代理时使用的固定IP,不过是不可能不用代理的了,这辈子是不可能的了
PROXY_NONE_URL = ""
# 请求超时，单位秒
TIMEOUT = 10
# 请求延时，单位秒
DOWNLOAD_DELAY = 1

# #固定User-Agent http user_agent，类型string
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'
# http cookies，类型string，例如：_ga=GA1.2.693027078.1517447891; _gid=GA1.2.390668217.1517447891
COOKIES = None
# http referer，类型string，例如：http://www.cnblogs.com/zy6103/p/
REFERER = None
# response的charset，类型string，根据网页的字符集设置，例如：utf-8、gb2312，GBK等
CHARSET= 'utf-8'
#固定头部
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'gzip',
    'Connection': 'close',
    'Referer': 'http://www.baidu.com/link?url=_andhfsjjjKRgEWkj7i9cFmYYGsisrnm2A-TN3XZDQXxvGsM9k9ZZSnikW2Yds4s&amp;amp;wd=&amp;amp;eqid=c3435a7d00146bd600000003582bfd1f'
    }


###############
# 任务调度模块配置,不要这种形式了,瞎JB用类来做模块
###############
#下载器模块
# DOWNLOADER_MODULE = 'Schedule.Downloader'
#针对CCGP页面解析器模块
# PARSERCCGPMODULE_MODULE = 'modules.ParserCCGPModule'
#资源存储管道通信模块
# PIPELINE_MODULE = 'modules.Pipeline'

###############
# url配置
###############
# 预处理地址，主要的目的是把ip发送给对面,如后期做登录验证可使用到
url_pre_execute = {
    # 'url': 'http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/preExecuteSearch!preExecuteSearch.do',
    'url': 'http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/pageIsUesd-pageUsed.shtml',
    'headers': {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        "Content-Length": "0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "http://www.pss-system.gov.cn",
        "Referer": "http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/tableSearch-showTableSearchIndex.shtml",
        "X-Requested-With": "XMLHttpRequest"
    }
}
# 获取收费的代理IP池
headersIpPoolCharge = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'gzip',
    'Connection': 'close',
    'Referer': 'http://www.bing.com/link?url=_andhfsjjjKRgEWkj7i9cFmYYGsisrnm2A-TN3XZDQXxvGsM9k9ZZSnikW2Yds4s&amp;amp;wd=&amp;amp;eqid=c3435a7d00146bd600000003582bfd1f'
}
urlIpPoolCharge = "http://tvp.daxiangdaili.com/ip/?tid=556415834988312&num=50000&delay=1&sortby=time"

#指定爬去的时间段
# 截取今天时间
nowTime = datetime.datetime.now().strftime('%Y-%m-%d').split('-')
strNowTime = nowTime[0]+'%3A'+nowTime[1]+'%3A'+nowTime[2]
# crawlerStartTime = '2018' + '%3A' + '06' + '%3A' + '12'
# crawlerEndTime = '2018' + '%3A' + '06' + '%3A' + '12'
crawlerStartTime = strNowTime
crawlerEndTime = strNowTime
###############
# 任务域名配置
###############
#
# [
#   {
#     "state":"ready",
#     "parser":"demo",
#     "request":"https://github.com/fightcat/ScrapyX",
#     "table":"demo_info",
#     "parent":{}
#   }
# ]