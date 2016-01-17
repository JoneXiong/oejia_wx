# coding=utf-8

from openerp.osv import osv
from openerp.http import request
from ..controllers import client

class im_chat_message(osv.Model):
    _inherit = 'im_chat.message'
    
    def _on_messages(self, uuid, session, from_uid, message_id, message_content, notifications):
        if hasattr(session, 'channel_id'):
            if session.channel_id.id==2 and from_uid:
                client.chat_send(request.db,uuid, message_content)