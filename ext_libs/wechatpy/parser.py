# -*- coding: utf-8 -*-
"""
    wechatpy.parser
    ~~~~~~~~~~~~~~~~
    This module provides functions for parsing WeChat messages

    :copyright: (c) 2014 by messense.
    :license: MIT, see LICENSE for more details.
"""
from __future__ import absolute_import, unicode_literals
import xmltodict

from wechatpy.messages import MESSAGE_TYPES, UnknownMessage
from wechatpy.events import EVENT_TYPES
from wechatpy.utils import to_text


def parse_message(xml):
    """
    Parse WeChat XML format messages
    :param xml: XML format messages
    :return: Parsed messages or events
    """
    if not xml:
        return
    message = xmltodict.parse(to_text(xml))['xml']
    message_type = message['MsgType'].lower()
    if message_type in ('event', 'device_event'):
        event_type = message['Event'].lower()
        # special event type for device_event
        if message_type == 'device_event':
            event_type = 'device_{event}'.format(event=event_type)
        if event_type == 'subscribe' and message.get('EventKey'):
            # Scan to subscribe with scene id event
            event_type = 'subscribe_scan'
            message['Event'] = event_type
            message['EventKey'] = message['EventKey'].replace('qrscene_', '')
        message_class = EVENT_TYPES.get(event_type, UnknownMessage)
    else:
        message_class = MESSAGE_TYPES.get(message_type, UnknownMessage)
    return message_class(message)
