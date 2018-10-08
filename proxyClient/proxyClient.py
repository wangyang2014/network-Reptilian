# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyClient
   Description :获取代理免费ip
   Author :       ZWZ
   date：          18-5-10
-------------------------------------------------
   Change Activity: 程序的代理决定使用https://github.com/jhao104/proxy_pool的代理池作为代理方式，
                   18-5-10:
-------------------------------------------------
"""
from conf.Setting import url_pre_execute, TIMEOUT, USE_PROXY, PROXY_URL, urlIpPoolCharge, headersIpPoolCharge, \
    PROXY_REMOTE_URL
import conf as conf
from utils.LogUtil import Log

__author__ = 'ZWZ'

import json

from requests.exceptions import RequestException, ReadTimeout
import requests
import queue
import time

def getIpProxyPool():
    """
    直接从本地获取免费ip代理
    :return: 可用的ip代理
    """
    if USE_PROXY is False:
        return None

    try:
        # Log.i('获取代理···')
        resp = requests.get(PROXY_URL, timeout=TIMEOUT)
        return resp.text
    except Exception as e:
        Log.e('无法获取代理信息，请确认代理系统是否启动')
        return None

def getIpProxyPoolFromeRemote():
    """
    直接从远程获取免费ip代理
    :return: 可用的ip代理
    """
    if USE_PROXY is False:
        return None

    try:
        # Log.i('获取代理···')
        resp = requests.get(PROXY_REMOTE_URL, timeout=TIMEOUT)
        return resp.text
    except Exception as e:
        Log.e('无法获取代理信息，请确认代理系统是否启动')
        return None


def notify_ip_address():
    """
    通知爬虫网站我们的ip地址，
    考虑到有些网站比较特别，每当有陌生ip地址时，都需要通过这个方法向网站发送一次请求先。
    :return:
    """
    resp = requests.post(url_pre_execute.get('url'), proxies=conf.PROXIES, timeout=TIMEOUT, cookies=conf.COOKIES)
    # logger.debug(resp.text)
    ip_address = json.loads(resp.text)
    if conf.PROXIES is not None:
        if ip_address.get('IP') == conf.PROXIES.get('http').split(':')[0]:
            return resp.text
        else:
            raise Exception('ip error')
    else:
        return resp.text

def get_proxy():
    """
    获取代理ip，并更新控制器PROXIES
    :return: 可用的ip代理
    """
    if USE_PROXY is False:
        return None

    try:
        Log.i('获取代理···')
        resp = requests.get(PROXY_URL, timeout=TIMEOUT)
        ip_address = resp.text
        proxies = {'http': ip_address, 'https': ip_address}
        # Log.i(proxies)
        PROXIES = proxies
        return PROXIES
    except Exception as e:
        Log.e('无法获取代理信息，请确认代理系统是否启动')
        return None

def update_proxy():
    """
    获取并校验代理ip地址
    :return:
    """
    if USE_PROXY:
        i = 0
        while True:
            try:
                get_proxy()
                notify_ip_address()
                return True
            except Exception:
                i += 1
                Log.e("代理获取失败，尝试重试，重试次数%s" % (i, ))
    else:
        Log.i('notify address')
        notify_ip_address()

def check_proxy(func):
    """
    校验代理的装饰器，使用情况较特殊，只针对请求超时异常
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        for i in range(5):
            try:
                resp = func(*args, **kwargs)
                return resp
            except RequestException:
                update_proxy()
        raise Exception('函数重试5次，仍无法成功')
    return wrapper


def getChargeIpPool():
    """
    获取收费ip代理池
    :return:返回代理ip队列
    """
    while (True):
        try:
            page = requests.get(urlIpPoolCharge, headers=headersIpPoolCharge, timeout=20)
            if (page.status_code == 200):
                break
        except Exception as e:
            time.sleep(10)
            print("error", e)
    # page.encoding = 'utf-8'

    page = str(page.content)
    iplist = page.split("\\r\\n")

    IpPool = queue.Queue()

    for ip in iplist:
        IpPool.put(ip)

    return IpPool

if __name__ == '__main__':
    print(getIpProxyPoolFromeRemote())
    # print(update_proxy())
    # print(getChargeIpPool().get())
    # update_cookies()
    # print(login())