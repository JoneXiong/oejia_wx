# coding=utf-8

from openerp.osv import osv
from openerp.http import request
from ..controllers import client

class im_chat_message(osv.Model):
    _inherit = 'im_chat.message'
    
    def _on_messages(self, uuid, session, from_uid, message_id, message_content, notifications):
        if hasattr(session, 'channel_id'):
            Param = request.env()['ir.config_parameter']
            wx_channel_id = Param.get_param('wx_channel') or 0
            wx_channel_id = int(wx_channel_id)
            if session.channel_id.id==wx_channel_id and from_uid:
                client.chat_send(request.db,uuid, message_content)