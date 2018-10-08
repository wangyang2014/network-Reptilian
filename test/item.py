# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     item
   Description :
   Author :       ZWZ
   date：          18-6-6
-------------------------------------------------
   Change Activity:
                   18-6-6:
-------------------------------------------------
"""
__author__ = 'ZWZ'

import scrapy


class BidinfoItem(scrapy.Item):
    title = scrapy.Field()  # 标题
    url = scrapy.Field()  # 链接
    label = scrapy.Field()  # 标签
    post_time = scrapy.Field()  # 发表时间
    content = scrapy.Field()  # 内容
    # define the fields for your item here like:
    # name = scrapy.Field()
