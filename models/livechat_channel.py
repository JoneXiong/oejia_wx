# coding=utf-8

import logging


from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class LivechatChannel(models.Model):

    _inherit = 'im_livechat.channel'

    @api.model
    def create_mail_channel(self, livechat_channel, anonymous_name, content, record_uuid):
        if record_uuid:
            return {'uuid': record_uuid}, self.get_wx_default_msg()
        return self.get_mail_channel(livechat_channel.id, anonymous_name), livechat_channel.get_wx_default_msg()

    def get_wx_default_msg(self):
        return self.default_message


