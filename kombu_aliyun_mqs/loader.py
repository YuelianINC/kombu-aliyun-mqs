#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Last modified: Zhong Gaohao (pkuember@gmail.com)


def load():
    from kombu import transport
    import kombu
    kombu.transport.TRANSPORT_ALIASES.update({"mqs": "kombu_aliyun_mqs.mqs:Transport"})
