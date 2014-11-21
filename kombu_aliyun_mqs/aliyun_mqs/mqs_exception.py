# -*- coding: utf-8 -*-

class MQSExceptionBase(Exception):
    def __init__(self, type, message):
        self.type = type
        self.message = message

    def get_info(self):
        return "(\"%s\" \"%s\")\n" % (self.type, self.message)

    def __str__(self):
        return "MQSExceptionBase  %s" % (self.get_info())

class MQSClientException(MQSExceptionBase):
    def __init__(self, type, message):
        MQSExceptionBase.__init__(self, type, message)

    def __str__(self):
        return "MQSClientException  %s" % (self.get_info())

class MQSServerException(MQSExceptionBase):
    def __init__(self, type, message, request_id, host_id):
        MQSExceptionBase.__init__(self, type, message)
        self.request_id = request_id
        self.host_id = host_id

    def __str__(self):
        return "MQSServerException  %s" % (self.get_info())
        
        
class MQSClientNetworkException(MQSClientException):
    def __init__(self, type, message):
        MQSClientException.__init__(self, type, message)

    def get_info(self):
        return "(\"%s\", \"%s\")\n" % (self.type, self.message)

    def __str__(self):
        return "MQSClientNetworkException  %s" % (self.get_info())

class MQSClientParameterException(MQSClientException):
    def __init__(self, type, message):
        MQSClientException.__init__(self, type, message)

    def __str__(self):
        return "MQSClientParameterException  %s" % (self.get_info())
