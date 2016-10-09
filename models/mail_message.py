# coding=utf-8

import logging


from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class mail_message(models.Model):
    _inherit = 'mail.message'
    
    wxcorp_notify = fields.Boolean('发送微信通知')
    
    
    
# class mail_notification(models.Model):
#     _inherit = 'mail.notification'
#     
#     def _notify(self, cr, uid, message_id, partners_to_notify=None, context=None,
#                 force_send=False, user_signature=True):
#         super(mail_notification, self)._notify(cr, uid, message_id, partners_to_notify=partners_to_notify, context=context, force_send=force_send, user_signature=user_signature)
#         Message = self.pool.get('mail.message')
#         message = Message.browse(cr, uid, message_id, context=context)
#         if message.wxcorp_notify:
#             from openerp import SUPERUSER_ID
#             user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context)
#             partners_to_notify.append(user.partner_id.id)
#             Partner = self.pool.get('res.partner')
#             for partner in Partner.browse(cr, SUPERUSER_ID, partners_to_notify, context=context):
#                 if partner.wxcorp_user_id:
#                     from ..rpc import corp_client
#                     _body = message.body.replace('<p>','').replace('</p>','')
#                     _content = u'%s\n%s'%(message.subject, _body) if message.subject else _body
#                     _head = u'%s 发送到 %s'%(message.author_id.name, message.record_name)
#                     try:
#                         corp_client.client.message.send_text(0, partner.wxcorp_user_id.userid, u'%s：%s'%(_head,_content) )
#                     except:
#                         pass
#                     _logger.info('>>>wxcorp_notify: %s'%str((message,partner)))


# class mail_compose_message(models.TransientModel):
#     _inherit = 'mail.compose.message'
#     
#     wxcorp_notify = fields.Boolean('发送微信通知')