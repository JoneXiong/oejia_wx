# coding=utf-8

import logging


from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class LivechatChannel(models.Model):

    _inherit = 'im_livechat.channel'


    @api.model
    def get_wx_default_msg(self):
        channel = self.env.ref('oejia_wx.channel_wx')
        return channel.default_message


