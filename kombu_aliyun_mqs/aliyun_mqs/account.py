# -*- coding: utf-8 -*-

from aliyun_mqs.mqs_client import MQSClient
from aliyun_mqs.mqs_request import *
from aliyun_mqs.queue import Queue

class Account:
    def __init__(self, host, accessId, accessKey):
        self.mAccessId = accessId
        self.mAccessKey = accessKey
        self.mQueueClient = MQSClient(host, accessId, accessKey)

    def set_queue_client(self, host):
        self.mQueueClient = MQSClient(host, self.mAccessId, self.mAccessKey)

    def get_queue_client(self):
        return self.mQueueClient

    def get_queue(self, queue_name):
        return Queue(queue_name, self.mQueueClient)

    def list_queue(self, prefix = "", ret_number = -1, marker = ""):
        req = ListQueueRequest(prefix, ret_number, marker)
        resp = ListQueueResponse()
        self.mQueueClient.list_queue(req, resp)
        return resp.queueurl_list, resp.next_marker

