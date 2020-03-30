# coding=utf-8
import logging

from werobot.utils import is_string
from wechatpy import create_reply
from wechatpy import replies

from openerp.http import request

_logger = logging.getLogger(__name__)

if True:
    def onclick(request, message):
        _name, action_id = message.key.split(',')
        action_id = int(action_id)
        if _name:
            action = request.env()[_name].sudo().browse(action_id)
            ret = action.get_wx_reply(message.source)
            if type(ret)==dict:
                media = ret
                media_type = media['media_type']
                media_id = media['media_id']
                if media_type=='image':
                    return replies.ImageReply(message=message, media_id=media_id)
                elif media_type=='voice':
                    return replies.VoiceReply(message=message, media_id=media_id)
                elif media_type=='video':
                    return replies.VideoReply(message=message, media_id=media_id)
                elif media_type=='news':
                    entry = request.entry
                    entry.wxclient.send_articles(message.source, media_id)
            else:
                return create_reply(ret, message=message)
