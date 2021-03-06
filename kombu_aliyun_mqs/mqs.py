#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Last modified: Zhong Gaohao (pkuember@gmail.com)
# from __future__ import absolute_import
import collections
import string

from kombu.transport import virtual
from kombu.async import get_event_loop
from kombu.five import Empty, range, string_t, text_t
from amqp.promise import transform, ensure_promise, promise
from kombu.transport.virtual import scheduling
from kombu.log import get_logger
from kombu.utils import cached_property
from kombu.utils.encoding import bytes_to_str, safe_str
from json import loads, dumps

from aliyun_mqs.mqs_client import MQSClient
from aliyun_mqs.queue import *
from aliyun_mqs.mqs_request import *

logger = get_logger(__name__)

# dots are replaced by dash, all other punctuation
# replaced by underscore.
# CHARS_REPLACE_TABLE = {
#     ord(c): 0x5f for c in string.punctuation if c not in '-_.'
# }
# CHARS_REPLACE_TABLE[0x2e] = 0x2d  # '.' -> '-'

#: SQS bulk get supports a maximum of 10 messages at a time.
MQS_MAX_MESSAGES = 10
class Channel(virtual.Channel):
    accessId = "4s6p9mKWQjaFJS73"
    accessKey = "YbbtIYlo1duxtB10usVviBhpst0m3o"
    mqs_client = MQSClient("http://dm00p375gl.mqs-cn-qingdao.aliyuncs.com", accessId, accessKey)
    _queue_cache = {}
    _noack_queues = set()
    _asynsqs = None
    _sqs = None
    default_visibility_timeout = 1800  # 30 minutes.
    default_region = 'us-east-1'
    default_wait_time_seconds = 10  # disabled see #198
    domain_format = 'kombu%(vhost)s'

    def __init__(self, *args, **kwargs):
        super(Channel, self).__init__(*args, **kwargs)

        # SQS blows up when you try to create a new queue if one already
        # exists with a different visibility_timeout, so this prepopulates
        # the queue_cache to protect us from recreating
        # queues that are known to already exist.
        logger.debug("create channel")
        req = ListQueueRequest()
        resp = ListQueueResponse()
        self.mqs_client.list_queue(req, resp)
        queueurl_list = resp.queueurl_list
        queues = [url.split('/')[-1] for url in queueurl_list]
        queuemeta_list = resp.queuemeta_list
        for queue in queues:
            self._queue_cache[queue] = Queue(queue, self.mqs_client)

        self._fanout_queues = set()
        # The drain_events() method stores extra messages in a local
        # Deque object. This allows multiple messages to be requested from
        # SQS at once for performance, but maintains the same external API
        # to the caller of the drain_events() method.
        self._queue_message_cache = collections.deque()

    def basic_consume(self, queue, no_ack, *args, **kwargs):
        logger.debug("basic_consume:" + queue)
        if no_ack:
            self._noack_queues.add(queue)
        return super(Channel, self).basic_consume(
            queue, no_ack, *args, **kwargs
        )

    def basic_cancel(self, consumer_tag):
        logger.debug("basic_cancel" + consumer_tag)
        if consumer_tag in self._consumers:
            queue = self._tag_to_queue[consumer_tag]
            self._noack_queues.discard(queue)
        return super(Channel, self).basic_cancel(consumer_tag)

    def drain_events(self, timeout=None):
        try:
            logger.debug("drain_events")
            """Return a single payload message from one of our queues.
            :raises Empty: if no messages available.
            """
            # If we're not allowed to consume or have no consumers, raise Empty
            if not self._consumers or not self.qos.can_consume():
                logger.debug("raise empty")
                raise Empty()
            message_cache = self._queue_message_cache

            # Check if there are any items in our buffer. If there are any, pop
            # off that queue first.
            logger.debug("first")
            try:
                return message_cache.popleft()
            except IndexError:
                logger.debug("indexerror 1")
                pass
            except Exception,e:
                logger.error(e)

            logger.debug(self._active_queues)
            res, queue = self._poll(self.cycle, timeout=timeout)
            # logger.debug(res)
            message_cache.extend((r, queue) for r in res)

            # Now try to pop off the queue again.
            logger.debug("second")
            try:
                m = message_cache.popleft()
                logger.debug("second:" + repr(m))
                return m
            except IndexError:
                logger.debug("indexerror 2")
                raise Empty()
            except Exception,e:
                logger.error(e)
        except Exception,e:
            import traceback
            logger.debug("54321")
            print str(e)
            traceback.print_exc()
            # print traceback.format_exc()
    #or
            # print sys.exc_info()[0]
            logger.debug("12345")

    def _reset_cycle(self):
        logger.debug("reset_cycle")
        """Reset the consume cycle.
        :returns: a FairCycle object that points to our _get_bulk() method
          rather than the standard _get() method. This allows for multiple
          messages to be returned at once from SQS (based on the prefetch
          limit).
        """
        self._cycle = scheduling.FairCycle(
            self._get, self._active_queues, Empty,
        )

    # def entity_name(self, name, table=CHARS_REPLACE_TABLE):
    #     """Format AMQP queue name into a legal SQS queue name."""
    #     return text_t(safe_str(name)).translate(table)

    def _new_queue(self, queue, **kwargs):
        """Ensure a queue with given name exists in SQS."""
        # logger.debug(type(queue))
        if isinstance(queue,unicode):
            queue = queue.encode('utf-8')
        # queue = str(queue)
        logger.debug("_new_queue:" + queue)
        # logger.debug(type(queue))
        queue = queue.replace('.','-')
        queue = queue.replace('@','-')
        if not isinstance(queue, string_t):
            return queue
        # Translate to SQS name for consistency with initial
        # _queue_cache population.
        queue = self.queue_name_prefix + queue
        try:
            logger.debug("_new_queue: normal")
            return self._queue_cache[queue]
        except KeyError:
            logger.debug("_new_queue: keyerror123")
            the_queue = Queue(queue, self.mqs_client)
            queue_meta = QueueMeta()
            queue_meta.set_visibilitytimeout(self.default_visibility_timeout)
            qurl = the_queue.create(queue_meta)
            logger.debug(qurl)
            self._queue_cache[queue] = the_queue
            return the_queue

    def _delete(self, queue, *args):
        logger.debug("_delete:" + queue)
        """delete queue by name."""
        super(Channel, self)._delete(queue)
        self._queue_cache.pop(queue, None)

    def _put(self, queue, message, **kwargs):
        """Put message onto queue."""
        logger.debug("_put" + queue + ' ' + dumps(message))
        q = self._new_queue(queue)
        m = Message()
        m.message_body = (dumps(message))
        q.send_message(m)

    # def _loop1(self, queue, _=None):
    #     self.hub.call_soon(self._schedule_queue, queue)
    #
    # def _schedule_queue(self, queue):
    #     if queue in self._active_queues:
    #         if self.qos.can_consume():
    #             self._get_async(
    #                 queue,
    #             )
    #         else:
    #             self._loop1(queue)

    def _message_to_python(self, message, queue_name, queue):
        payload = loads(bytes_to_str(message.get_body()))
        if queue_name in self._noack_queues:
            queue.delete_message(message.receipt_handle)
        else:
            payload['properties']['delivery_info'].update({
                'mqs_message': message, 'mqs_queue': queue,
            })
        return [payload]

    def _messages_to_python(self, messages, queue):
        """Convert a list of SQS Message objects into Payloads.
        This method handles converting SQS Message objects into
        Payloads, and appropriately updating the queue depending on
        the 'ack' settings for that queue.
        :param messages: A list of SQS Message objects.
        :param queue: String name representing the queue they came from
        :returns: A list of Payload objects
        """
        q = self._new_queue(queue)
        return [self._message_to_python(m, queue, q) for m in messages]


    def _get(self, queue):
        logger.debug('_get:' + queue)
        """Try to retrieve a single message off ``queue``."""
        q = self._new_queue(queue)
        message = q.receive_message()
        if message:
            return self._message_to_python(message, queue, q)
        raise Empty()

    def _get_async(self, queue, count=1, callback=None):
        q = self._new_queue(queue)
        return self._get_from_mqs(
            q, count=count, mqs_client=self.mqs_client,
            callback=transform(self._on_messages_ready, callback, q, queue),
        )

    def _on_messages_ready(self, queue, qname, messages):
        logger.debug('on_message_ready')
        if messages:
            callbacks = self.connection._callbacks
            for raw_message in messages:
                message = self._message_to_python(raw_message, qname, queue)
                callbacks[qname](message)

    def _get_from_mqs(self, queue,
                      count=1, mqs_client=None, callback=None):
        """Retrieve and handle messages from SQS.
        Uses long polling and returns :class:`~amqp.promise`.
        """
        logger.debug('get_from_mqs')
        mqs_client = mqs_client if mqs_client is not None else queue.mqs_client
        return queue.receive_message()
        # return connection.receive_message(
        #     queue, number_messages=count,
        #     wait_time_seconds=self.wait_time_seconds,
        #     callback=callback,
        # )

    def _restore(self, message,
                 unwanted_delivery_info=('mqs_message', 'mqs_queue')):
        logger.debug('restore')
        for unwanted_key in unwanted_delivery_info:
            # Remove objects that aren't JSON serializable (Issue #1108).
            message.delivery_info.pop(unwanted_key, None)
        return super(Channel, self)._restore(message)

    def basic_ack(self, delivery_tag):
        logger.debug('basic_ack')
        delivery_info = self.qos.get(delivery_tag).delivery_info
        try:
            queue = delivery_info['mqs_queue']
        except KeyError:
            pass
        else:
            queue.delete_message(delivery_info['mqs_message'])
        super(Channel, self).basic_ack(delivery_tag)

    def _size(self, queue):
        """Return the number of messages in a queue."""
        q = self._new_queue(queue)
        attr = q.get_attributes()
        res = attr.active_messages
        logger.debug('_size:'+ str(res))
        return res

    def _purge(self, queue):
        logger.debug('purge')
        """Delete all current messages in a queue."""
        q = self._new_queue(queue)
        # SQS is slow at registering messages, so run for a few
        # iterations to ensure messages are deleted.
        size = 0
        for i in range(10):
            size += q.count()
            if not size:
                break
        q.clear()
        return size

    # @property
    # def asynmqs(self):
    #     if self._asynmqs is None:
    #         self._asynmqs = self._aws_connect_to(
    #             AsyncSQSConnection, _asynsqs.regions(),
    #         )
    #     return self._asynsqs

    @property
    def transport_options(self):
        return self.connection.client.transport_options

    @cached_property
    def queue_name_prefix(self):
        return self.transport_options.get('queue_name_prefix', '')

    @cached_property
    def visibility_timeout(self):
        return (self.transport_options.get('visibility_timeout') or
                self.default_visibility_timeout)

    @cached_property
    def supports_fanout(self):
        return False

    @cached_property
    def region(self):
        return self.transport_options.get('region') or self.default_region

    @cached_property
    def wait_time_seconds(self):
        return self.transport_options.get('wait_time_seconds',
                                          self.default_wait_time_seconds)
import socket
class Transport(virtual.Transport):
    Channel = Channel

    polling_interval = 1
    wait_time_seconds = 0
    default_port = None
    connection_errors = (
        virtual.Transport.connection_errors +
        (socket.error,)
    )
    channel_errors = (
        virtual.Transport.channel_errors
    )
    driver_type = 'mqs'
    driver_name = 'mqs'

    # implements = virtual.Transport.implements.extend(
    #     async=False,
    #     exchange_type=frozenset(['direct']),
    # )