# coding=utf-8

import logging


from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class LivechatChannel(models.Model):

    _inherit = 'im_livechat.channel'

    @api.model
    def create_mail_channel(self, livechat_channel_id, anonymous_name, content):
        return self.get_mail_channel(livechat_channel_id, anonymous_name), self.get_wx_default_msg()

    @api.model
    def get_wx_default_msg(self):
        channel = self.env.ref('oejia_wx.channel_wx')
        return channel.default_message


