# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     pipelines
   Description :
   Author :       ZWZ
   date：          18-6-6
-------------------------------------------------
   Change Activity:
                   18-6-6:
-------------------------------------------------
"""
__author__ = 'ZWZ'

from scrapy import signals
import json
import codecs
import sys
import importlib
importlib.reload(sys)

class BidinfoPipeline(object):
    def process_item(self, item, spider):
        name = item['title']
        file_name = str(name)+".txt"
        cpath='/home/longma/Desktop/code/webCrawler/log/webCrawler'+'/'
        path=cpath+file_name
        print(path)
        fp = open(path,'w')
        fp.write(item['title']+'\n')
        fp.write(item['url']+'\n')
        fp.write(item['label']+'\n')
        fp.write(item['post_time']+'\n')
        fp.write(item['content'])
        fp.close()
         #with opne("a.txt","a") as f:
             #f.write(log)

        return item
