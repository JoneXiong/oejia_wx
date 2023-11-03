# coding=utf-8
import logging

from wechatpy import replies

from odoo.http import request

_logger = logging.getLogger(__name__)

if True:
    def onclick(request, message):
        _name, action_id = message.key.split(',')
        action_id = int(action_id)
        if _name:
            action = request.env()[_name].sudo().browse(action_id)
            ret = action.get_wx_reply(message.source)
            entry = request.entry
            return entry.create_reply(ret, message)
