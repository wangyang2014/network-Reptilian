# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     UrlUtil
   Description :
   Author :       ZWZ
   date：          18-5-10
-------------------------------------------------
   Change Activity:
                   18-5-10:
-------------------------------------------------
"""
__author__ = 'ZWZ'

import re

class UrlUtil():

    @staticmethod
    def getdomain(urlname):
        """
        切割根域名
        :param urlname:
        :return:
        """
        domain = None
        pattern =  r'htt(p|ps):\/\/(\w+\.)+\w+'
        pattern = re.compile(pattern)
        Keyvalue = pattern.search(urlname)
        if Keyvalue == None:
            Keyvalue = "can't know url-Domian"
        else:
            Keyvalue = Keyvalue.group()
            domain = Keyvalue
        return domain

    @staticmethod
    def isLegalUrl(url):
        """
        验证url的正确性
        :param url:
        https://nihao.com/dddni.jpg(^(https?|ftp|file)://.+$ )
        www.nihao.com/dddni.jpg
        http://www.nihao.com/dddni.jpg
        :return:
        """
        if re.match(r'^((https?|ftp)://|(www|ftp)\.)[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+([/?].*)?$', url):
            return True
        else:
            return False
