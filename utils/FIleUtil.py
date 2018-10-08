# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     FIleUtil
   Description : 文件處理工具類
   Author :       ZWZ
   date：          18-5-10
-------------------------------------------------
   Change Activity:
                   18-5-10:
-------------------------------------------------
"""

__author__ = 'ZWZ'



class FileUtil:
    def __init__(self, filename, mode):
        self.__filename = filename
        self.__file = open(self.__filename, mode, encoding='utf8')

    def __del__(self):
        self.__file.close()

    def writeLine(self, strLine):
        self.__file.write(strLine + "\n")
        self.__file.flush()


