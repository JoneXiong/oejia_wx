# coding=utf-8

import logging


from odoo import models, fields, api
from odoo.http import request

_logger = logging.getLogger(__name__)


class LivechatChannel(models.Model):

    _inherit = 'im_livechat.channel'

    ctype = fields.Selection([('wx_gzh','微信公众号'), ('wx_corp','企业微信'), ('wx_app','微信小程序'), ('normal','普通')], string='类型', default='normal')

    @api.model
    def create_mail_channel(self, livechat_channel, anonymous_name, content, record_uuid, entry=None):
        if record_uuid:
            return {'uuid': record_uuid}, livechat_channel.get_wx_default_msg()
        return self.get_mail_channel(livechat_channel.id, anonymous_name), livechat_channel.get_wx_default_msg()

    def get_wx_default_msg(self):
        return self.default_message

    @api.model
    def get_mail_channel(self, livechat_channel_id, anonymous_name):
        return request.env["im_livechat.channel"].with_context(lang=False).with_user(self.env.ref('base.public_partner').id).browse(livechat_channel_id)._open_livechat_mail_channel(anonymous_name)
