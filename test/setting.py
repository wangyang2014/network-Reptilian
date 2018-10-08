# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     setting
   Description :
   Author :       ZWZ
   date：          18-6-6
-------------------------------------------------
   Change Activity:
                   18-6-6:
-------------------------------------------------
"""
__author__ = 'ZWZ'

BOT_NAME = 'bidinfo'
SPIDER_MODULES = ['bidinfo.spiders']
NEWSPIDER_MODULE = 'bidinfo.spiders'
LOG_LEVEL = 'INFO'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'bidinfo (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 1

ITEM_PIPELINES = {
    'bidinfo.pipelines.BidinfoPipeline': 300,
}
