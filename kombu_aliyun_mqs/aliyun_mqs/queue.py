# -*- coding: utf-8 -*-

from aliyun_mqs.mqs_request import *


class Queue:
    def __init__(self, queue_name, mqs_client): 
        self.queue_name = queue_name
        self.mqs_client = mqs_client
        self.set_encoding(True)

    def set_encoding(self, encoding):
        self.encoding = encoding
        
    def create(self, queue_meta):
        req = CreateQueueRequest(self.queue_name, queue_meta.visibility_timeout, queue_meta.maximum_message_size, queue_meta.message_retention_period, queue_meta.delay_seconds, queue_meta.polling_wait_seconds)
        resp = CreateQueueResponse()
        self.mqs_client.create_queue(req, resp)
        return resp.queue_url

    def get_attributes(self):
        req = GetQueueAttributesRequest(self.queue_name)
        resp = GetQueueAttributesResponse()
        self.mqs_client.get_queue_attributes(req, resp)
        queue_meta = QueueMeta()
        self.__resp2meta__(queue_meta, resp)
        return queue_meta

    def set_attributes(self, queue_meta):
        req = SetQueueAttributesRequest(self.queue_name, queue_meta.visibility_timeout, queue_meta.maximum_message_size, queue_meta.message_retention_period, queue_meta.delay_seconds, queue_meta.polling_wait_seconds)
        resp = SetQueueAttributesResponse
        self.mqs_client.set_queue_attributes(req, resp)
    
    def delete(self):
        req = DeleteQueueRequest(self.queue_name)
        resp = DeleteQueueResponse()
        self.mqs_client.delete_queue(req, resp)

    def send_message(self, message):
        req = SendMessageRequest(self.queue_name, message.message_body, message.delay_seconds, message.priority, self.encoding)
        resp = SendMessageResponse()
        self.mqs_client.send_message(req, resp)
        return self.__send_resp2msg__(resp)

    def peek_message(self):
        req = PeekMessageRequest(self.queue_name)
        resp = PeekMessageResponse()
        self.mqs_client.peek_message(req, resp)
        return self.__peek_resp2msg__(resp)

    def receive_message(self):
        req = ReceiveMessageRequest(self.queue_name, self.encoding)
        resp = ReceiveMessageResponse()
        self.mqs_client.receive_message(req, resp)
        msg = self.__recv_resp2msg__(resp)
        return msg
   
    def delete_message(self, receipt_handle):
        req = DeleteMessageRequest(self.queue_name, receipt_handle)
        resp = DeleteMessageResponse()
        self.mqs_client.delete_message(req, resp)

    def change_message_visibility(self, reciept_handle, visibility_timeout):
        req = ChangeMessageVisibilityRequest(self.queue_name, reciept_handle, visibility_timeout)
        resp = ChangeMessageVisibilityResponse()
        self.mqs_client.change_message_visibility(req, resp)
        return self.__changevis_resp2msg__(resp)


    def __resp2meta__(self, queue_meta, resp):
        queue_meta.visibility_timeout = resp.visibility_timeout
        queue_meta.maximum_message_size = resp.maximum_message_size
        queue_meta.message_retention_period = resp.message_retention_period
        queue_meta.delay_seconds = resp.delay_seconds
        queue_meta.polling_wait_seconds = resp.polling_wait_seconds

        queue_meta.active_messages = resp.active_messages
        queue_meta.inactive_messages = resp.inactive_messages
        queue_meta.delay_messages = resp.delay_messages
        queue_meta.create_time = resp.create_time
        queue_meta.last_modify_time = resp.last_modify_time
        queue_meta.queue_name = resp.queue_name

    def __send_resp2msg__(self, resp):
        msg = Message()
        msg.message_id = resp.message_id
        msg.message_body_md5 = resp.message_body_md5
        return msg
        
    def __peek_resp2msg__(self, resp):
        msg = self.__send_resp2msg__(resp)
        msg.dequeue_count = resp.dequeue_count
        msg.enqueue_time = resp.enqueue_time
        msg.first_dequeue_time = resp.first_dequeue_time
        msg.message_body = resp.message_body
        msg.priority = resp.priority
        return msg
       
    def __recv_resp2msg__(self, resp):
        msg = self.__peek_resp2msg__(resp)
        msg.receipt_handle = resp.receipt_handle
        msg.next_visible_time = resp.next_visible_time
        return msg

    def __changevis_resp2msg__(self, resp):
        msg = Message()
        msg.receipt_handle = resp.receipt_handle
        msg.next_visible_time = resp.next_visible_time
        return msg

class QueueMeta:
    def __init__(self):
        self.visibility_timeout = 30
        self.maximum_message_size = 65536
        self.message_retention_period = 345600
        self.delay_seconds = 0
        self.polling_wait_seconds = 0

        self.active_messages = -1
        self.inactive_messages = -1
        self.delay_messages = -1
        self.create_time = -1
        self.last_modify_time = -1
        self.queue_name = ""

    def set_visibilitytimeout(self, visibility_timeout):
        self.visibility_timeout = visibility_timeout

    def set_maximum_message_size(self, maximum_message_size):
        self.maximum_message_size = maximum_message_size
    
    def set_message_retention_period(self, message_retention_period):
        self.message_retention_period = message_retention_period

    def set_delay_seconds(self, delay_seconds):
        self.delay_seconds = delay_seconds

    def set_polling_wait_seconds(self, polling_wait_seconds):
        self.polling_wait_seconds = polling_wait_seconds

class Message:
    def __init__(self, message_body = ""):
        self.message_body = message_body
        self.delay_seconds = 0
        self.priority = 8

        self.message_id = ""
        self.message_body_md5 = ""

        self.dequeue_count = -1
        self.enqueue_time = -1
        self.first_dequeue_time = -1

        self.receipt_handle = ""
        self.next_visible_time = 1

    def set_delayseconds(self, delay_seconds):
        self.delay_seconds = delay_seconds

    def set_priority(self, priority):
        self.priority = priority

    def get_body(self):
        return self.message_body