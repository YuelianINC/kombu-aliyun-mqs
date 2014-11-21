#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from account import Account
from aliyun_mqs.queue import *


if __name__ == "__main__":
    accessId = "<AccessKeyId>"
    accessKey = "<AccessKeySecret>"
    mqs_client = MQSClient("http://<QueueOwnerId>.mqs-<Region>.aliyuncs.com", "<AccessKeyId>", "<AccessKeySecret>")

    #create queue
    queue_name = "MyQueue"
    my_queue = Queue(queue_name, mqs_client)
    queue_meta = QueueMeta()
    queue_meta.set_visibilitytimeout(100)
    queue_meta.set_maximum_message_size(10240)
    queue_meta.set_message_retention_period(3600)
    queue_meta.set_delay_seconds(3)
    queue_meta.set_polling_wait_seconds(10)
    try:
        queue_url = my_queue.create(queue_meta)
        print "Create Queue Succeed:%s\n" % queue_url
    except MQSExceptionBase, e:
        print "Create Queue Fail:", e
        sys.exit(1)

    #set queue attributes
    queue_name = "MyQueue"
    my_queue = Queue(queue_name, mqs_client)
    queue_meta = QueueMeta()
    queue_meta.set_visibilitytimeout(70)
    queue_meta.set_maximum_message_size(9999)
    queue_meta.set_message_retention_period(1234)
    queue_meta.set_delay_seconds(2)
    queue_meta.set_polling_wait_seconds(12)
    try:
        queue_url = my_queue.set_attributes(queue_meta)
        print "Set Queue Attributes Succeed!"
    except MQSExceptionBase, e:
        print "Set Queue Attributes Fail:", e
        sys.exit(1)

    #get queue attributes
    queue_name = "MyQueue"
    my_queue = Queue(queue_name, mqs_client)
    try:
        queue_meta = my_queue.get_attributes()
        print "Get Queue Attributes Succeed! Queue Name: %s" % queue_meta.queue_name
        print "visibility_timeout is %s" % queue_meta.visibility_timeout
        print "maximum_message_size is %s" % queue_meta.maximum_message_size
        print "delay_seconds is %s" % queue_meta.delay_seconds
        print "polling_wait_seconds is %s" % queue_meta.polling_wait_seconds
        print "active_messages is %s" % queue_meta.active_messages
        print "inactive_messages is %s" % queue_meta.inactive_messages
        print "delay_messages is %s" % queue_meta.delay_messages
        print "create_time is %s" % queue_meta.create_time
        print "last_modify_time is %s" % queue_meta.last_modify_time
    except MQSExceptionBase, e:
        print "Get Queue Attributes Fail:", e
        sys.exit(1)

    #delete queue
    queue_name = "MyQueue"
    my_queue = Queue(queue_name, mqs_client)
    try:
        my_queue.delete()
        print "Delete Queue Succeed!"
    except MQSExceptionBase, e:
        print "Delete Queue Fail:", e
        sys.exit(1)

    #list queue
    account = Account("http://bdpz7z5yno.mqs-test171.aliyuncs.com:8087", accessId, accessKey)
    try:
        marker = ""
        while(True):
            queue_url_list, next_marker = account.list_queue(prefix = "", ret_number = 10, marker = marker)
            print "List Queue Succeed!"
            for queue_url in queue_url_list:
                print queue_url
            if(next_marker == ""):
                break
            marker = next_marker
    except MQSExceptionBase, e:
        print "List Queue Fail:", e
        sys.exit(1)

    #send message
    queue_name = "MyQueue"
    my_queue = Queue(queue_name, mqs_client)
    msg_body = "I am test Message."
    message = Message(msg_body)
    message.set_delayseconds(2)
    message.set_priority(10)
    try:
        send_msg = my_queue.send_message(message)
        print "Send Message Succeed.\nMessageBody:%s\nMessageId:%s\nMessageBodyMd5:%s\n" % (msg_body, send_msg.message_id, send_msg.message_body_md5)
    except MQSExceptionBase, e:
        print "Send Message Fail:", e
        sys.exit(1)

    #receive message
    queue_name = "MyQueue"
    my_queue = Queue(queue_name, mqs_client)
    try:
        recv_msg = my_queue.receive_message()
        print "Receive Message Succeed!"
        print "message_id is %s" % recv_msg.message_id
        print "message_body_md5 is %s" % recv_msg.message_body_md5
        print "message_body is %s" % recv_msg.message_body
        print "dequeue_count is %s" % recv_msg.dequeue_count
        print "enqueue_time is %s" % recv_msg.enqueue_time
        print "first_dequeue_time is %s" % recv_msg.first_dequeue_time
        print "priority %s" % recv_msg.priority
        print "next_visible_time %s" % recv_msg.next_visible_time
        print "receipt_handle is %s" % recv_msg.receipt_handle
    except MQSExceptionBase, e:
        print "Receive Message Fail:", e
        sys.exit(1)

    #delete message
    queue_name = "MyQueue"
    my_queue = Queue(queue_name, mqs_client)
    try:
        my_queue.delete_message(recv_msg.receipt_handle)
        print "Delete Message Succeed."
    except MQSExceptionBase, e:
        print "Delete Message Fail:", e
        sys.exit(1)

    #peek message
    queue_name = "MyQueue"
    my_queue = Queue(queue_name, mqs_client)
    try:
        peek_msg = my_queue.peek_message()
        print "Peek Message Succeed!"
        print "message_id is %s" % peek_msg.message_id
        print "message_body_md5 is %s" % peek_msg.message_body_md5
        print "message_body is %s" % peek_msg.message_body
        print "dequeue_count is %s" % peek_msg.dequeue_count
        print "enqueue_time is %s" % peek_msg.enqueue_time
        print "first_dequeue_time is %s" % peek_msg.first_dequeue_time
        print "priority %s" % peek_msg.priority
    except MQSExceptionBase, e:
        print "Peek Message Fail:", e
        sys.exit(1)

    #change message visibility
    queue_name = "MyQueue"
    my_queue = Queue(queue_name, mqs_client)
    try:
        change_msg_vis = my_queue.change_message_visibility(recv_msg.receipt_handle, 35)
        print "Change Message Visibility Succeed!"
        print "receipt_handle is %s" % change_msg_vis.receipt_handle
        print "next_visible_time is %s" % change_msg_vis.next_visible_time
    except MQSExceptionBase, e:
        print "Change Message Visibility Fail:", e
        sys.exit(1)
