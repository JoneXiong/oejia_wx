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

    handler_url = fields.Char('消息对接URL', readonly=True, compute='_compute_handler_url', help='这里显示当前用于小程序消息对接的接口URL，无需修改，请将其填入小程序后台相应的地方')


    @api.multi
    def write(self, vals):
        result = super(WxAppConfig, self).write(vals)
        from ..rpc import app_client
        app_client.AppEntry().init(self.env)
        return result

    @api.one
    def _compute_handler_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        self.handler_url = '%s/app_handler'%base_url

    @api.model
    def get_cur(self):
        return self.env.ref('oejia_wx.wx_app_config_data_1')

    @api.multi
    def name_get(self):
        return [(e.id, u'小程序对接设置') for e in self]

