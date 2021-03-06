# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     HttpUtil
   Description : 访问http/https
   Author :       ZWZ
   date：          18-5-9
-------------------------------------------------
   Change Activity:
                   18-5-9:
-------------------------------------------------
"""
import json

__author__ = 'ZWZ'

import os
import requests
from selenium.webdriver.common.proxy import ProxyType
from utils.LogUtil import Log
import demjson

class HttpUtil:
    '''
    访问http/https
    1.获取response
    2.下载文件
    '''
    def __init__(self):
        pass

    @staticmethod
    def get_header(url, params=None, headers=None, cookies=None, proxies=None):
        '''
        发送http head请求
        :param url:str 请求的url
        :return: dict header值
        '''
        html = None
        try:
            r = requests.get(url)
            html=r.headers
        except Exception as e:
            Log.e("http get header failed -> " + str(e))
        finally:
            pass
        return html

    @staticmethod
    def get_html(url, params=None, headers=None, cookies=None, proxies=None, charset='UTF-8'):
        '''
        发送http get请求
        :param url:str 请求的url
        :param params:dict 参数
        :param headers:dict 自定义请求头
        :param cookies:dict 网站cookies
        :param proxies:dict 代理
        :return: str 返回的str文本
        '''
        html = None
        try:
            r = requests.get(url, params=params, headers=headers, cookies=cookies, proxies=proxies)
            r.encoding = charset
            html=r.text
        except Exception as e:
            Log.e("http get html failed -> " + str(e))
        finally:
            pass
        return html

    @staticmethod
    def get_json(url, params=None, headers=None, cookies=None, proxies=None, charset='UTF-8'):
        '''
        发送http get请求
        :param url:str 请求的url
        :param params:dict 参数
        :param headers:dict 自定义请求头
        :param cookies:dict 网站cookies
        :param proxies:dict 代理
        :return: json 返回的json对象
        '''
        html = None
        try:
            r = requests.get(url, params=params, headers=headers, cookies=cookies, proxies=proxies)
            r.encoding = charset
            html = r.json()
        except Exception as e:
            Log.e("http get json failed -> " + str(e))
        finally:
            pass
        return html

    @staticmethod
    def get_file(file_name, url, params=None, headers=None, cookies=None, proxies=None):
        '''
        发送http get请求文件
        :return:
        '''
        html = True
        try:
            r = requests.get(url, params=params, headers=headers, cookies=cookies, proxies=proxies)
            with open(file_name, 'wb') as fd:
                for chunk in r.iter_content(512):
                    fd.write(chunk)
        except Exception as e:
            Log.e("http get file failed -> " + str(e))
            html=False
        finally:
            pass
        return html

    @staticmethod
    def post_html(url, data=None, headers=None, cookies=None, proxies=None, charset='UTF-8'):
        '''
        发送http post请求
        :param url:str 请求的url
        :param data:dict post的数据
        :param headers:dict 自定义请求头
        :return: str 返回的str文本
        '''
        html = None
        try:
            r = requests.post(url, data=data, headers=headers, cookies=cookies, proxies=proxies)
            r.encoding = charset
            html = r.text
        except Exception as e:
            Log.e("http post html failed -> " + str(e))
        finally:
            pass
        return html

    @staticmethod
    def gets_html(url, params=None, headers=None, cookies=None, proxies=None, charset='UTF-8'):
        '''
        发送https get请求
        :param url:str 请求的url
        :param params:dict 参数
        :param headers:dict 自定义请求头
        :param cookies:dict 网站cookies
        :param proxies:dict 代理
        :return: str 返回的str文本
        '''
        html = None
        try:
            r = requests.get(url, params=params, headers=headers, cookies=cookies, proxies=proxies, verify=False)
            r.encoding = charset
            html = r.text
        except Exception as e:
            Log.e("https get html failed -> " + str(e))
        finally:
            pass
        return html

    @staticmethod
    def posts_html(url, data=None, headers=None, cookies=None, proxies=None, charset='UTF-8'):
        '''
        发送https post请求
        :param url:str 请求的url
        :param data:dict post的数据
        :param headers:dict 自定义请求头
        :return: str 返回的str文本
        '''
        html=None
        try:
            r = requests.post(url, data=data, headers=headers, cookies=cookies, proxies=proxies, verify=False)
            r.encoding = charset
            html=r.text
        except Exception as e:
            Log.e("https post html failed -> " + str(e))
        finally:
            pass
        return html

    @staticmethod
    def deep_get(url,headers=None,proxies=None):
        '''
        深度get，使用PhantomJS处理javascript和302跳转
        :param url:
        :param headers: dict，http header，例：
            headers = { 'Accept': '*/*',
                        'Accept-Language': 'en-US,en;q=0.8',
                        'Cache-Control': 'max-age=0',
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
                        'Connection': 'keep-alive',
                        'Cookie':'_ga=GA1.2.693027078.1517447891; _gid=GA1.2.390668217.1517447891'，
                        'Referer':'http://www.baidu.com/'
            }
        :param proxies: dict，代理，例：
            proxies = {
                    "http": "http://127.0.0.1:8888"
            }
        :return: data,cookies
        '''
        from selenium import webdriver
        from selenium.webdriver import DesiredCapabilities
        desired_capabilities = DesiredCapabilities.PHANTOMJS.copy()
        #自定义header
        if headers is not None:
            for key, value in headers.iteritems():
                desired_capabilities['phantomjs.page.customHeaders.{}'.format(key)] = value
        #自定义proxy
        if proxies is not None:
            proxy = webdriver.Proxy()
            proxy.proxy_type = ProxyType.MANUAL
            proxy.http_proxy = proxies['http']
            proxy.add_to_capabilities(desired_capabilities)
        #构建driver
        driver = webdriver.PhantomJS(desired_capabilities=desired_capabilities,service_log_path=os.path.devnull)
        #访问url
        driver.get(url)
        # 获取html页面源码
        data = driver.page_source
        # 获得cookie信息
        cookies = driver.get_cookies()
        driver.quit()
        return data,cookies

if __name__ == '__main__':
    charset = 'utf-8'
    headers = {"User-Agent":'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'}
    proxies = "103.78.213.147:80"
    protocol = 'https' if 'https' in proxies else 'http'
    proxiesmmm = {protocol: proxies}
    print(proxiesmmm)
    url=r'http://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index=7890&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=1&dbselect=bidx&kw=&start_time=2013%3A04%3A09&end_time=2014%3A04%3A08&timeType=6&displayZone=&zoneId=&pppStatus=0&agentName='
    baidu = 'https://www.baidu.com/'
    # html = requests.get(url, headers=headers, proxies=proxiesmmm, timeout=2)
    # html=HttpUtil.get_html(url, headers=headers, proxies=proxiesmmm, cookies=None, charset=charset)
    # html = HttpUtil.gets_html('https://www.cnblogs.com/guqing/p/6512246.html')
    # html = HttpUtil.get_header(url, headers=headers, proxies=proxiesmmm, cookies=None)
    html = requests.get(url, headers=headers, proxies=proxiesmmm, timeout=2)  # ,proxies=proxiesmmm,stream=True
    reqheaders = html.headers
    if "application" in reqheaders["Content-Type"]:
        print("application")
    elif "text" in reqheaders["Content-Type"]:
        print("text")
    print(html)
