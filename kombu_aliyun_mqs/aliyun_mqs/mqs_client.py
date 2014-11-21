# -*- coding: utf-8 -*-

import time
import hashlib
import hmac

from mqs_xml_handler import *
from mqs_tool import *
from mqs_http import *


GET_ACCOUNT_STATUS = 200
CREATE_QUEUE_STATUS = 201
DELETE_QUEUE_STATUS = 204
LIST_QUEUE_STATUS = 200
SET_QUEUE_ATTRIBUTES_STATUS = 200
SEND_MESSAGE_STATUS = 201
RECEIVE_MESSAGE_STATUS = 200
DELETE_MESSAGE_STATUS = 204
PEEK_MESSAGE_STATUS = 200
CHANGE_MESSAGE_VISIBILITY_STATUS = 200
SET_POLICY_STATUS = 204
DELETE_POLICY_STATUS = 204
GET_POLICY_STATUS = 200

class MQSClient:
    __max_listener_number = 50
    def __init__(self, host, accessId, accessKey, version = "2014-07-08"):
        self.mHost = host
        self.mAccessId = accessId
        self.mAccessKey = accessKey
        self.mHttp = MQSHttp()
        self.mVersion = version

    def set_connection_timeout(self, connTimeout):
        self.mHttp.set_connection_timeout(connTimeout)

#===============================================sdk===============================================#
       
    def create_queue(self, req, resp):
        #check parameter
        CreateQueueValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s" % req.queue_name)
        req_inter.data = QueueEncoder.encode(req)
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.mHttp.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(CREATE_QUEUE_STATUS, resp_inter, resp)
        if resp.error_data == "":
            resp.queue_url = resp.header["location"]

    def delete_queue(self, req, resp):
        #check parameter
        DeleteQueueValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s" % req.queue_name)
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.mHttp.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(DELETE_QUEUE_STATUS, resp_inter, resp)

    def list_queue(self, req, resp):
        #check parameter
        ListQueueValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/")
        if req.prefix != "":
            req_inter.header["x-mqs-prefix"] = req.prefix
        if req.ret_number != -1:
            req_inter.header["x-mqs-ret-number"] = str(req.ret_number)
        if req.marker != "":
            req_inter.header["x-mqs-marker"] = str(req.marker)
        if req.with_meta:
            req_inter.header["x-mqs-with-meta"] = "true"
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.mHttp.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(LIST_QUEUE_STATUS, resp_inter, resp)
        if resp.error_data == "":
            resp.queueurl_list, resp.next_marker, resp.queuemeta_list = ListQueueDecoder.decode(resp_inter.data, req)

    def set_queue_attributes(self, req, resp):
        #check parameter
        SetQueueAttrValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s?metaoverride=true" % (req.queue_name))
        req_inter.data = QueueEncoder.encode(req, False)
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.mHttp.send_request(req_inter)

        #handle result, make response 
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(SET_QUEUE_ATTRIBUTES_STATUS, resp_inter, resp)

    def get_queue_attributes(self, req, resp):
        #check parameter
        GetQueueAttrValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s" % req.queue_name)
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.mHttp.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(SET_QUEUE_ATTRIBUTES_STATUS, resp_inter, resp)
        if resp.error_data == "":
            queue_attr = GetQueueAttrDecoder.decode(resp_inter.data)
            resp.active_messages = string.atol(queue_attr["ActiveMessages"])
            resp.create_time = string.atol(queue_attr["CreateTime"])
            resp.delay_messages = string.atol(queue_attr["DelayMessages"])
            resp.delay_seconds = string.atol(queue_attr["DelaySeconds"])
            resp.inactive_messages = string.atol(queue_attr["InactiveMessages"])
            resp.last_modify_time = string.atol(queue_attr["LastModifyTime"])
            resp.maximum_message_size = string.atol(queue_attr["MaximumMessageSize"])
            resp.message_retention_period = string.atol(queue_attr["MessageRetentionPeriod"])
            resp.queue_name = queue_attr["QueueName"]
            resp.visibility_timeout = string.atol(queue_attr["VisibilityTimeout"])
            resp.polling_wait_seconds = string.atol(queue_attr["PollingWaitSeconds"])

    def send_message(self, req, resp):
        #check parameter
        SendMessageValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, uri = "/%s/messages" % req.queue_name)
        req_inter.data = MessageEncoder.encode(req)
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.mHttp.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(SEND_MESSAGE_STATUS, resp_inter, resp)
        if resp.error_data == "":
            resp.message_id, resp.message_body_md5 = SendMessageDecoder.decode(resp_inter.data)

    def receive_message(self, req, resp):
        #check parameter
        ReceiveMessageValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s/messages" % req.queue_name)
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.mHttp.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(RECEIVE_MESSAGE_STATUS, resp_inter, resp)
        if resp.error_data == "":
            data = RecvMessageDecoder.decode(resp_inter.data, req)
            self.make_recvresp(data, resp)

    def delete_message(self, req, resp):
        #check parameter
        DeleteMessageValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s/messages?ReceiptHandle=%s" % (req.queue_name, req.receipt_handle))
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.mHttp.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(DELETE_MESSAGE_STATUS, resp_inter, resp)

    def peek_message(self, req, resp):
        #check parameter
        PeekMessageValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s/messages?peekonly=true" % req.queue_name)
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.mHttp.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(PEEK_MESSAGE_STATUS, resp_inter, resp)
        if resp.error_data == "":
            data = PeekMessageDecoder.decode(resp_inter.data, req)
            self.make_peekresp(data, resp)

    def change_message_visibility(self, req, resp):
        #check parameter
        ChangeMsgVisValidator.validate(req)

        #make request internal
        req_inter = RequestInternal(req.method, "/%s/messages?ReceiptHandle=%s&VisibilityTimeout=%d" % (req.queue_name, req.receipt_handle, req.visibility_timeout))
        self.build_header(req, req_inter)

        #send request
        resp_inter = self.mHttp.send_request(req_inter)

        #handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(CHANGE_MESSAGE_VISIBILITY_STATUS, resp_inter, resp)
        if resp.error_data == "":
            resp.receipt_handle, resp.next_visible_time = ChangeMsgVisDecoder.decode(resp_inter.data)

    
###################################################################################################        
#----------------------internal-------------------------------------------------------------------#
    def build_header(self, req, req_inter):
        if req_inter.data != "":
            req_inter.header["content-md5"] = base64.b64encode(hashlib.md5(req_inter.data).hexdigest())
            req_inter.header["content-type"] = "text/xml;charset=UTF-8"
        req_inter.header["x-mqs-version"] = self.mVersion
        req_inter.header["host"] = self.mHost
        req_inter.header["date"] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        req_inter.header["Authorization"] = self.get_signature(req_inter.method, req_inter.header, req_inter.uri)

    def get_signature(self,method,headers,resource):
        content_md5 = self.get_element('content-md5', headers)
        content_type = self.get_element('content-type', headers)
        date = self.get_element('date', headers)
        canonicalized_resource = resource
        canonicalized_mqs_headers = ""
        if len(headers) > 0:
            x_header_list = headers.keys()
            x_header_list.sort()
            for k in x_header_list:
                if k.startswith('x-mqs-'):
                    canonicalized_mqs_headers += k + ":" + headers[k] + "\n"
        string_to_sign = "%s\n%s\n%s\n%s\n%s%s" % (method, content_md5, content_type, date, canonicalized_mqs_headers, canonicalized_resource)
        h = hmac.new(self.mAccessKey, string_to_sign, hashlib.sha1)
        signature = base64.b64encode(h.digest())
        signature = "MQS " + self.mAccessId + ":" + signature
        return signature

    def get_element(self, name, container):
        if name in container:
            return container[name]
        else:
            return ""

    def check_status(self, expect_status, resp_inter, resp):
        if resp_inter.status == expect_status or (resp_inter.status >= 300 and resp_inter.status < 400):
            resp.error_data = ""
        else:
            resp.error_data = resp_inter.data
            if resp_inter.status >= 400 and resp_inter.status <= 600:
                error = ErrorDecoder.decode(resp.error_data)
                raise MQSServerException(error["Code"], error["Message"], error["RequestId"], error["HostId"])
            else:
                raise MQSClientNetworkException("UnkownError", resp_inter.data)

    def make_recvresp(self, data, resp):
        resp.dequeue_count = string.atol(data["DequeueCount"])
        resp.enqueue_time = string.atol(data["EnqueueTime"])
        resp.first_dequeue_time = string.atol(data["FirstDequeueTime"])
        resp.message_body = data["MessageBody"]
        resp.message_id = data["MessageId"]
        resp.message_body_md5 = data["MessageBodyMD5"]
        resp.next_visible_time = string.atol(data["NextVisibleTime"])
        resp.receipt_handle = data["ReceiptHandle"]
        resp.priority = string.atol(data["Priority"])

    def make_peekresp(self, data, resp):
        resp.dequeue_count = string.atol(data["DequeueCount"])
        resp.enqueue_time = string.atol(data["EnqueueTime"])
        resp.first_dequeue_time = string.atol(data["FirstDequeueTime"])
        resp.message_body = data["MessageBody"]
        resp.message_id = data["MessageId"]
        resp.message_body_md5 = data["MessageBodyMD5"]
        resp.priority = string.atol(data["Priority"])
