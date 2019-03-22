# -*- coding: utf-8 -*-

from odoo import models, fields, api

from .menu_about_models import ACTION_OPTION

class WxConfig(models.Model):

    _name = 'wx.config'
    _description = u'公众号配置'

    action = fields.Reference(string='关注后的自动回复', selection=ACTION_OPTION)

    @api.multi
    def write(self, vals):
        result = super(WxConfig, self).write(vals)
        from ..controllers import client
        entry = client.wxenv(self.env)
        if self.action:
            entry.subscribe_auto_msg = self.action.get_wx_reply()
        return result

    @api.one
    def _compute_handler_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        self.handler_url = '%s/app_handler'%base_url

    @api.model
    def get_cur(self):
        return self.env.ref('oejia_wx.wx_config_data_1')

    @api.multi
    def name_get(self):
        return [(e.id, u'公众号配置') for e in self]

