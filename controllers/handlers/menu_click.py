# coding=utf-8
from werobot.utils import is_string
from werobot.reply import create_reply

from openerp.http import request

def main(robot):

    @robot.click
    def onclick(message, session):
        _name, action_id = message.key.split(',')
        action_id = int(action_id)
        if _name:
            action = request.env()[_name].sudo().browse(action_id)
            ret = action.get_wx_reply()
            if is_string(ret):
                return create_reply(ret, message=message)
            elif isinstance(ret, list):
                return create_reply(ret, message=message)
            elif type(ret)==dict:
                media = ret
                media_type = media['media_type']
                media_id = media['media_id']
                from werobot.replies import ImageReply, VoiceReply, VideoReply, ArticlesReply
                if media_type=='image':
                    return ImageReply(message=message, media_id=media_id).render()
                elif media_type=='voice':
                    return VoiceReply(message=message, media_id=media_id).render()
                elif media_type=='video':
                    return VideoReply(message=message, media_id=media_id).render()
                elif media_type=='news':
                    from .. import client
                    entry = client.wxenv(request.env)
                    entry.wxclient.send_news_message(message.source, media_id)
