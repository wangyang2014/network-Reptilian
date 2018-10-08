# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     spider
   Description :
   Author :       ZWZ
   date：          18-6-6
-------------------------------------------------
   Change Activity:
                   18-6-6:
-------------------------------------------------
"""
from test.item import BidinfoItem

__author__ = 'ZWZ'

import scrapy
import sys
from scrapy.http import Request
import re


class BidnewsSpider(scrapy.Spider):
    name = 'bidnews'
    allowed_domains = ['ccgp.gov.cn']

    def start_requests(self):
        #http://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index=2&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=0&dbselect=bidx&kw=&start_time=2018%3A06%3A11&end_time=2018%3A06%3A11&timeType=6&displayZone=&zoneId=&pppStatus=0&agentName=
        # kws=['客流预测','wifi探针','公交线网优化','公交线网','公交运行','公交走廊',
        # '公交专用道','OD','智慧交通','智能交通','公共交通','智能交通管理',
        # '智慧城市顶层设计','运行指数','智慧城市规划','多规合一','出行特征',
        # '人流应急管理','交通枢纽','交通仿真','交通优化','TransCAD']
        # kws = sys.argv[1]
        # kws = kws.strip('[\']').split("', '")
        # start_time = sys.argv[2].replace('-', '%3A')
        # end_time = sys.argv[3].replace('-', '%3A')

        start_time = '2018' + '%3A' + '06' + '%3A' + '04'
        end_time = '2018' + '%3A' + '06' + '%3A' + '11'
        all_urls = "http://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index=2&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=0&dbselect=bidx&kw=&start_time={0}&end_time={1}&timeType=6&displayZone=&zoneId=&pppStatus=0&agentName=".format(
                start_time, end_time)
        for url in all_urls:
            yield Request(url, self.parse)

    def parse(self, response):
        page = (int(response.xpath('//div[@class="vT_z"]/div[1]/div/p[1]/span[2]/text()').extract()[0]) // 20) + 2
        for i in range(1, page):
            url = str(response.url)
            x = 'page_index=' + str(i)
            url = re.sub(r'page_index=(.)', x, url)
            yield Request(url, callback=self.get_message)

    def get_message(self, response):
        item = BidinfoItem()
        item['title'] = str(response.xpath('//h2[@class="tc"]/text()').extract()[0]).replace('/', '')
        item['url'] = str(response.url)
        item['label'] = '|'.join(response.xpath('//div[@class="vT_detail_nav_lks"]/a/text()').extract()[1:3])
        item['post_time'] = str(response.xpath('//span[@id="pubTime"]/text()').extract()[0])
        item['content'] = ''.join(
            [i.strip() for i in response.xpath('//div[@class="vT_detail_content w760c"]//text()').extract()])
        yield item


