# coding=utf-8

import logging
import datetime

from openerp.osv import osv
from openerp.http import request
from openerp import models, fields, api

_logger = logging.getLogger(__name__)

class im_chat_message(models.Model):
    _inherit = 'im_chat.message'
    
    def _on_messages(self, uuid, session, from_uid, message_id, message_content, notifications):
        if hasattr(session, 'channel_id'):
            Param = request.env()['ir.config_parameter']
            wx_channel_id = Param.get_param('wx_channel') or 0
            wx_channel_id = int(wx_channel_id)
            Corp_Channel_id = Param.get_param('Corp_Channel') or 0
            Corp_Channel_id = int(Corp_Channel_id)
            Corp_Agent = Param.get_param('Corp_Agent') or 0
            Corp_Agent = int(Corp_Agent)
            if from_uid:
                session_channel_id = session.channel_id.id
                if session_channel_id and session_channel_id==wx_channel_id:
                    from ..controllers import client
                    client.chat_send(request.db, uuid, message_content)
                elif session_channel_id and session_channel_id==Corp_Channel_id:
                    from ..rpc import corp_client
                    corp_client.chat_send(request.db, uuid, message_content)
                else:
                    session_users = session.user_ids
                    from_user = [e for e in session_users if e.id==from_uid][0]
                    for user in session.user_ids:
                        if user.id==from_uid:
                            continue
                        _partner = user.partner_id
                        if _partner.wxcorp_user_id:
                            from ..rpc import corp_client

                            _key = '%s-%s'%(request.db, user.id)
                            new_flag = False
                            if _key in corp_client.UID_UUID:
                                _data = corp_client.UID_UUID[_key]
                                _now = datetime.datetime.now()
                                if _now - _data['last_time']<=  datetime.timedelta(seconds=10*60):
                                    if _data['from'] == from_uid:
                                        message_content = u'%s：%s'%(from_user.name, message_content)
                                        new_flag = True
                                    else:
                                        message_content = u'%s：%s'%(from_user.name, message_content)
                                else:
                                    message_content = u'%s：%s\n (10分钟内可直接回复)'%(from_user.name, message_content)
                                    new_flag = True
                            else:
                                message_content = u'%s：%s\n (10分钟内可直接回复)'%(from_user.name, message_content)
                                new_flag = True
                                # 全新
                            if new_flag:
                                if _key not in corp_client.UID_UUID:
                                    corp_client.UID_UUID[_key] = {}
                                corp_client.UID_UUID[_key]['from'] = from_uid
                                corp_client.UID_UUID[_key]['last_time'] = datetime.datetime.now()
                                corp_client.UID_UUID[_key]['uuid'] = uuid
                            try:
                                corp_client.client.message.send_text(Corp_Agent, _partner.wxcorp_user_id.userid, message_content)
                            except:
                                pass
                    
                
                