# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     kafkaUrlinformation
   Description : url話題
   Author :       ZWZ
   date：          18-5-10
-------------------------------------------------
   Change Activity:
                   18-5-10:
-------------------------------------------------
"""
import json

from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka.errors import KafkaError

from callback import AsycThread
from entity.URLinformation import URLinformation
from test.kafkaConf import localKafka_setting
from utils.LogUtil import Log

__author__ = 'ZWZ'


class localKafkaUrlinformation():
    def __init__(self):
        self.producer = self.__setproducer()
        self.consumer = self.__setconsumer()
        self.URL_inf = URLinformation()

    # def __del__(self):
    #     self.producer.close()
    #     self.consumer.close()

    def __setproducer(self):
        """
        返回生产父链接话题的生产者对象
        :return:
        """
        conf = localKafka_setting
        producer = KafkaProducer(bootstrap_servers=conf['bootstrap_servers'])
        return producer

    def __setconsumer(self):
        """
        返回消费父链接话题的消费者对象
        :return:
        """
        conf = localKafka_setting
        try:
            consumer = KafkaConsumer(bootstrap_servers=conf['bootstrap_servers'],
                                     group_id=conf['consumer_id'])
        except KafkaError as e:
            Log.e(e + 'kafkaConsumer failed')

        return consumer

    # @AsycThread.async
    def producerUrl(self, strurl):
        """
        生产父链接
        :param strurl:
        """
        try:
            conf = localKafka_setting
            future = self.producer.send(conf['topic_name'], bytes(strurl, 'ASCII'))
            self.producer.flush()
            future.get()
        except KafkaError as e:
            #TODO 异常kafka.errors.KafkaTimeoutError: KafkaTimeoutError: Failed to update metadata after 60.0 secs处理
            #https://stackoverflow.com/questions/48261501/kafka-errors-kafkatimeouterror-kafkatimeouterror-failed-to-update-metadata-aft
            self.producer.close()
            if self.producer is None:
                self.producer = self.__setproducer()
            Log.e(e+'send message failed')
            pass

    def consumerurl(self):
        """
        消费父链接
        :param queueDictData:
        """
        conf = localKafka_setting
        self.consumer.subscribe((conf['topic_name']))
        # TODO 这里阻塞是消费者连接超时，底层SDK主动调用断线重连API,监听数据回调(永久死循环,无JB优化了)
        for message in self.consumer:
            jsondata = str(message.value, "utf-8")
            Log.i(jsondata)
            # try:
            #     dictdata = json.loads(jsondata)
            # except Exception as e:
            #     Log.e(e + jsondata)
            #     continue

    # @AsycThread.async
    def producterUUID(self, strurl):
        """
        生产ggcp话题的uuid
        :param strurl:
        """
        try:
            conf = localKafka_setting
            #TODO 抛出异常kafka.errors.KafkaTimeoutError: KafkaTimeoutError: Failed to update metadata after 60.0 secs.
            future = self.producer.send(conf['topic_name_ccgp'], bytes(strurl, 'ASCII'))
            self.producer.flush()
            future.get()
        except KafkaError as e:
            self.producer.close()
            if self.producer is None:
                self.producer = self.__setproducer()
            Log.e(e+'send message failed')
            pass


    def setURL_inf(self, dictdata):
        """
        url数据模型
        :param dictdata:
        """
        self.URL_inf.dict2class(dictdata)

    def getURL_inf(self):
        """
        url对外接口
        :return:
        """
        return self.URL_inf



















