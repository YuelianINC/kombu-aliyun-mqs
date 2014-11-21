# -*- coding: utf-8 -*-

class RequestBase:
    def __init__(self):
        self.method = ""

class ResponseBase():
    def __init__(self):
        self.status = -1
        self.header = {}
        self.error_data = ""

class CreateQueueRequest(RequestBase):
    def __init__(self, queue_name, visibility_timeout = -1, maximum_message_size = -1, message_retention_period = -1, delay_seconds = -1, polling_wait_seconds = -1):
        RequestBase.__init__(self)
        self.queue_name = queue_name
        self.visibility_timeout = visibility_timeout
        self.maximum_message_size = maximum_message_size
        self.message_retention_period = message_retention_period
        self.delay_seconds = delay_seconds
        self.polling_wait_seconds = polling_wait_seconds
        self.method = "PUT"

class CreateQueueResponse(ResponseBase):
    def __init__(self):
        ResponseBase.__init__(self)
        self.queue_url = ""

class DeleteQueueRequest(RequestBase):
    def __init__(self, queue_name):
        RequestBase.__init__(self)
        self.queue_name = queue_name
        self.method = "DELETE"

class DeleteQueueResponse(ResponseBase):
    def __init__(self):
        ResponseBase.__init__(self)
        
class ListQueueRequest(RequestBase):
    def __init__(self, prefix = "", ret_number = -1, marker = "", with_meta = False):
        RequestBase.__init__(self)
        self.prefix = prefix
        self.ret_number = ret_number
        self.marker = marker
        self.with_meta = with_meta
        self.method = "GET"
    
class ListQueueResponse(ResponseBase):
    def __init__(self):
        ResponseBase.__init__(self)
        self.queueurl_list = []
        self.next_marker = ""
        self.queuemeta_list = []

class SetQueueAttributesRequest(RequestBase):
    def __init__(self, queue_name, visibility_timeout = -1, maximum_message_size = -1, message_retention_period = -1, delay_seconds = -1, polling_wait_seconds = -1):
        RequestBase.__init__(self)
        self.queue_name = queue_name
        self.visibility_timeout = visibility_timeout
        self.maximum_message_size = maximum_message_size
        self.message_retention_period = message_retention_period
        self.delay_seconds = delay_seconds
        self.polling_wait_seconds = polling_wait_seconds
        self.method = "PUT"

class SetQueueAttributesResponse(ResponseBase):
    def __init__(self):
        ResponseBase.__init__(self)

class GetQueueAttributesRequest(RequestBase):
    def __init__(self, queue_name):
        RequestBase.__init__(self)
        self.queue_name = queue_name
        self.method = "GET"
        
class GetQueueAttributesResponse(ResponseBase):
    def __init__(self):
        ResponseBase.__init__(self)
        self.active_messages = -1
        self.create_time = -1
        self.delay_messages = -1
        self.delay_seconds = -1
        self.inactive_messages = -1
        self.last_modify_time = -1
        self.maximum_message_size = -1
        self.message_retention_period = -1
        self.queue_name = ""
        self.visibility_timeout = -1
        self.polling_wait_seconds = -1

class SendMessageRequest(RequestBase):
    def __init__(self, queue_name, message_body, delay_seconds = -1, priority = -1, base64encode = True):
        RequestBase.__init__(self)
        self.queue_name = queue_name
        self.message_body = message_body
        self.delay_seconds = delay_seconds
        self.priority = priority
        self.base64encode = base64encode
        self.method = "POST"

class SendMessageResponse(ResponseBase):
    def __init__(self):
        ResponseBase.__init__(self)
        self.message_id = ""
        self.message_body_md5 = ""

class PeekMessageRequest(RequestBase):
    def __init__(self, queue_name, base64decode = True):
        RequestBase.__init__(self)
        self.queue_name = queue_name
        self.base64decode = base64decode
        self.method = "GET"

class PeekMessageResponse(ResponseBase):
    def __init__(self):
        ResponseBase.__init__(self)
        self.dequeue_count = -1
        self.enqueue_time = -1
        self.first_dequeue_time = -1
        self.message_body = ""
        self.message_id = ""
        self.message_body_md5 = ""
        self.priority = -1

class ReceiveMessageRequest(RequestBase):
    def __init__(self, queue_name, base64decode = True):
        RequestBase.__init__(self)
        self.queue_name = queue_name
        self.base64decode = base64decode
        self.method = "GET"

class ReceiveMessageResponse(PeekMessageResponse):
    def __init__(self):
        PeekMessageResponse.__init__(self)
        self.next_visible_time = -1
        self.receipt_handle = ""

class DeleteMessageRequest(RequestBase):
    def __init__(self, queue_name, receipt_handle):
        RequestBase.__init__(self)
        self.queue_name = queue_name
        self.receipt_handle = receipt_handle
        self.method = "DELETE"

class DeleteMessageResponse(ResponseBase):
    def __init__(self):
        ResponseBase.__init__(self)

class ChangeMessageVisibilityRequest(RequestBase):
    def __init__(self, queue_name, receipt_handle, visibility_timeout):
        RequestBase.__init__(self)
        self.queue_name = queue_name
        self.receipt_handle = receipt_handle
        self.visibility_timeout = visibility_timeout
        self.method = "PUT"

class ChangeMessageVisibilityResponse(ResponseBase):
    def __init__(self):
        ResponseBase.__init__(self)
        self.receipt_handle = ""
        self.next_visible_time = -1
