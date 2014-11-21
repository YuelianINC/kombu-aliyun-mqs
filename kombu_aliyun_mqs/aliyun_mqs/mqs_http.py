# -*- coding: utf-8 -*-

from httplib import HTTPConnection

from aliyun_mqs.mqs_exception import *
from mqs_tool import DataTypeConversion


class MyHTTPConnection(HTTPConnection):
    def __init__(self, host, port=None, strict=None):
        HTTPConnection.__init__(self, host, port, strict)
        self.request_length = 0

    def send(self, str):
        HTTPConnection.send(self, str)
        self.request_length += len(str)

    def request(self, method, url, body=None, headers={}):
        self.request_length = 0
        HTTPConnection.request(self, method, url, body, headers)

class MQSHttp:
    def __init__(self, connTimeout = 10):
        self.mConnTimeout = connTimeout
        self.mRequestSize = 0
        self.mRespSize = 0

    def set_connection_timeout(self, connTimeout):
        self.mConnTimeout = connTimeout
 
    def send_request(self, req_inter):
        if req_inter.header["host"].startswith("http://"):
            if req_inter.header["host"].endswith("/"):
                req_inter.header["host"] =  req_inter.header["host"][:-1]
            req_inter.header["host"] = req_inter.header["host"][len("http://"):]
            try:
                conn = MyHTTPConnection(req_inter.header["host"])
                conn.request(req_inter.method, req_inter.uri, req_inter.data, req_inter.header)
                conn.sock.settimeout(self.mConnTimeout)
                http_resp = conn.getresponse()
                headers = DataTypeConversion().tuplelist2dict(http_resp.getheaders())
                resp_inter = ResponseInternal(status = http_resp.status, header = headers, data = http_resp.read())
                self.mRequestSize = conn.request_length
                self.mRespSize = len(resp_inter.data)
                conn.close()
                return resp_inter
            except Exception,e:
                conn.close()
                raise MQSClientNetworkException("NetWorkException", str(e)) #raise netException
        else:
            raise MQSClientParameterException("InvalidHost", "Only support http prototol. Invalid host:%s" % req_inter.header["host"])

class RequestInternal:
    def __init__(self, method = "", uri = "", header = None, data = ""):
        if header == None:
            header = {}
        self.method = method
        self.uri = uri
        self.header = header
        self.data = data 

    def __str__(self):
        return "method: %s\nuri: %s\nheader: %s\ndata: %s\n" % (self.method, self.uri, self.header, self.data)

class ResponseInternal:
    def __init__(self, status = 0, header = None, data = ""):
        if header == None:
            header = {}
        self.status = status
        self.header = header
        self.data = data

    def __str__(self):
        return "status: %s\nheader: %s\ndata: %s" % (self.status, self.header, self.data)
