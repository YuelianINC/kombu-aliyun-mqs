# -*- coding: utf-8 -*-

import xml.dom.minidom
import base64

from aliyun_mqs.mqs_exception import *


def create_child_element(doc, parent, name):
    child = doc.createElement(name)
    parent.appendChild(child)
    
    return child

def get_value_string(node):
    return str(node.childNodes[0].nodeValue.strip());

    
class EncoderBase:
    @staticmethod
    def insert_if_valid(item_name, item_value, invalid_value, data_dic):
        if item_value != invalid_value:
            data_dic[item_name] = item_value

    @staticmethod
    def dic_to_xml(tagName, dataDic):
        doc = xml.dom.minidom.Document()
        tagNode = doc.createElement(tagName)
        tagNode.attributes["xmlns"] = "http://mqs.aliyuncs.com/doc/v1/"
        doc.appendChild(tagNode)
        if(dataDic != {}):
            for k,v in dataDic.items():
                keyNode = doc.createElement(k)
                tagNode.appendChild(keyNode)
                valueNode = doc.createTextNode(v)
                keyNode.appendChild(valueNode)
        else:
            nullNode = doc.createTextNode("")
            tagNode.appendChild(nullNode)
        return doc.toxml("utf-8")

class QueueEncoder(EncoderBase):
    @staticmethod
    def encode(data, has_slice = True):
        queue = {}
        EncoderBase.insert_if_valid("VisibilityTimeout", str(data.visibility_timeout), "-1", queue)
        EncoderBase.insert_if_valid("MaximumMessageSize", str(data.maximum_message_size), "-1", queue)
        EncoderBase.insert_if_valid("MessageRetentionPeriod", str(data.message_retention_period), "-1", queue)
        EncoderBase.insert_if_valid("DelaySeconds", str(data.delay_seconds), "-1", queue)
        EncoderBase.insert_if_valid("PollingWaitSeconds", str(data.polling_wait_seconds), "-1", queue)
        return EncoderBase.dic_to_xml("Queue", queue)

class MessageEncoder(EncoderBase):
    @staticmethod
    def encode(data):
        message = {}
        if data.base64encode:
            msgbody = base64.b64encode(data.message_body)
        else:
            msgbody = data.message_body
        EncoderBase.insert_if_valid("MessageBody", msgbody, "", message)
        EncoderBase.insert_if_valid("DelaySeconds", str(data.delay_seconds), "-1", message)
        EncoderBase.insert_if_valid("Priority", str(data.priority), "-1", message)
        return EncoderBase.dic_to_xml("Message", message)

#-------------------------------------------------decode-----------------------------------------------------#
class DecoderBase:
    @staticmethod
    def xml_to_nodes(tag_name, xml_data):
        if xml_data == "":
            raise MQSClientNetworkException("RespDataDamaged", "Xml data is \"\"!")
            
        try:
            dom = xml.dom.minidom.parseString(xml_data)
        except Exception, e:
            raise MQSClientNetworkException("RespDataDamaged", xml_data)
            
        nodelist = dom.getElementsByTagName(tag_name)
        if not nodelist:
            raise MQSClientNetworkException("RespDataDamaged", "No element with tag name '%s'" % tag_name)
            
        return nodelist[0].childNodes
            
    
    @staticmethod
    def xml_to_dic(tag_name, xml_data, data_dic):
        for node in DecoderBase.xml_to_nodes(tag_name, xml_data):
            if ( node.nodeName != "#text" and node.childNodes != []):
                data_dic[node.nodeName] = str(node.childNodes[0].nodeValue.strip())

class CreateQueueDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data):
        data_dic = {}
        DecoderBase.xml_to_dic("Queue", xml_data, data_dic)

        if "QueueURL" in data_dic.keys():
            queue_url = data_dic["QueueURL"]
            return str(queue_url)
        else:
            raise MQSClientNetworkException("RespDataDamaged", xml_data)
       
class ListQueueDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data, req):
        queueurl_list = []
        queuemeta_list = []
        next_marker = ""
        if (xml_data != ""):
            try:
                dom = xml.dom.minidom.parseString(xml_data)
            except Exception, e:
                raise MQSClientNetworkException("RespDataDamaged", xml_data)
            nodelist = dom.getElementsByTagName("Queues")
            if ( nodelist != [] and nodelist[0].childNodes != []):
                for node in nodelist[0].childNodes:
                    if ( node.nodeName == "Queue" and node.childNodes != []):
                        queuemeta = {}
                        for node1 in node.childNodes:
                            if ( node1.nodeName == "QueueURL" and node1.childNodes != []):
                                queueurl_list.append(str(node1.childNodes[0].nodeValue.strip()))
                            if ( req.with_meta and node1.nodeName != "#text" and node1.childNodes != []):
                                queuemeta[str(node1.nodeName)] = str(node1.childNodes[0].nodeValue.strip())
                        if req.with_meta:
                            queuemeta_list.append(queuemeta)
                    elif ( node.nodeName == "NextMarker" and node.childNodes != []):
                        next_marker = str(node.childNodes[0].nodeValue.strip())
        else:
            raise MQSClientNetworkException("RespDataDamaged", "Xml data is \"\"!")
        return queueurl_list, str(next_marker), queuemeta_list

class GetQueueAttrDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data):
        data_dic = {}
        DecoderBase.xml_to_dic("Queue", xml_data, data_dic)
        key_list = ["ActiveMessages", "CreateTime", "DelayMessages", "DelaySeconds", "InactiveMessages", "LastModifyTime", "MaximumMessageSize", "MessageRetentionPeriod", "QueueName", "VisibilityTimeout", "PollingWaitSeconds"]
        for key in key_list:
            if key not in data_dic.keys():
                raise MQSClientNetworkException("RespDataDamaged", xml_data)
        return data_dic

class SendMessageDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data):
        data_dic = {}
        DecoderBase.xml_to_dic("Message", xml_data, data_dic)
        key_list = ["MessageId", "MessageBodyMD5"]
        for key in key_list:
            if key not in data_dic.keys():
                raise MQSClientNetworkException("RespDataDamaged", xml_data)
        return data_dic["MessageId"], data_dic["MessageBodyMD5"]

class RecvMessageDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data, req):
        data_dic = {}
        DecoderBase.xml_to_dic("Message", xml_data, data_dic)
        key_list = ["DequeueCount", "EnqueueTime", "FirstDequeueTime", "MessageBody", "MessageId", "MessageBodyMD5", "NextVisibleTime", "ReceiptHandle", "Priority"]
        for key in key_list:
            if key not in data_dic.keys():
                raise MQSClientNetworkException("RespDataDamaged", xml_data)
        if req.base64decode:
            decode_str = base64.b64decode(data_dic["MessageBody"])
            data_dic["MessageBody"] = decode_str
        return data_dic

class PeekMessageDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data, req):
        data_dic = {}
        DecoderBase.xml_to_dic("Message", xml_data, data_dic)
        key_list = ["DequeueCount", "EnqueueTime", "FirstDequeueTime", "MessageBody", "MessageId", "MessageBodyMD5", "Priority"]
        for key in key_list:
            if key not in data_dic.keys():
                raise MQSClientNetworkException("RespDataDamaged", xml_data)
        if req.base64decode:
            decode_str = base64.b64decode(data_dic["MessageBody"])
            data_dic["MessageBody"] = decode_str
        return data_dic

class ChangeMsgVisDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data):
        data_dic = {}
        DecoderBase.xml_to_dic("ChangeVisibility", xml_data, data_dic)

        if "ReceiptHandle" in data_dic.keys() and "NextVisibleTime" in data_dic.keys():
            return data_dic["ReceiptHandle"], data_dic["NextVisibleTime"]
        else:
            raise MQSClientNetworkException("RespDataDamaged", xml_data)

class ErrorDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data):
        data_dic = {}
        DecoderBase.xml_to_dic("Error", xml_data, data_dic)
        key_list = ["Code", "Message", "RequestId", "HostId"]
        for key in key_list:
            if key not in data_dic.keys():
                raise MQSClientNetworkException("RespDataDamaged", xml_data)
        return data_dic
