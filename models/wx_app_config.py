# -*- coding: utf-8 -*-

from odoo import models, fields, api


class WxAppConfig(models.Model):

    _name = 'wx.app.config'
    _description = u'小程序对接设置'
    _rec_name = 'app_id'

    app_id = fields.Char('AppID')
    secret = fields.Char('Secret')

    token = fields.Char('Token')
    aeskey = fields.Char('AESKey')

    handler_url = fields.Char('消息对接URL', readonly=True, compute='_compute_handler_url')


    @api.multi
    def write(self, vals):
        result = super(WxAppConfig, self).write(vals)
        from ..rpc import app_client
        app_client.AppEntry().init(self.env)
        return result

    @api.one
    def _compute_handler_url(self):
        self.handler_url = ''

    @api.model
    def get_cur(self):
        return self.env.ref('oejia_wx.wx_app_config_data_1')

