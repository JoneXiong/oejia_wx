# -*- coding: utf-8 -*-

from odoo import models, fields, api

from .menu_about_models import ACTION_OPTION

def generate_token(length=''):
    import string
    import random
    try:
        from secrets import choice
    except ImportError:
        from random import choice
    if not length:
        length = random.randint(3, 32)
    length = int(length)
    assert 3 <= length <= 32
    letters = string.ascii_letters + string.digits
    return ''.join(choice(letters) for _ in range(length))

class WxConfig(models.Model):

    _name = 'wx.config'
    _description = u'公众号配置'

    action = fields.Reference(string='关注后的自动回复', selection=ACTION_OPTION)

    wx_appid = fields.Char('AppId', )
    wx_AppSecret = fields.Char('AppSecret', )
    wx_AccessToken = fields.Char('当前AccessToken', readonly=True)

    wx_url = fields.Char('URL', readonly=True, compute='_compute_wx_url', help='请将此URL拷贝填到公众号官方后台，并确保公网能访问该地址')
    wx_token = fields.Char('Token', default=generate_token, help='必须为英文或数字，长度为3-32字符, 系统默认自动生成，也可自行修改')
    wx_aeskey = fields.Char('EncodingAESKey', default='')

    @api.multi
    def write(self, vals):
        result = super(WxConfig, self).write(vals)
        from ..rpc import wx_client
        wx_client.WxEntry().init(self.env, from_ui=True)
        return result

    @api.multi
    def _compute_wx_url(self):
        objs = self
        for self in objs:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            self.wx_url = '%s/wx_handler'%base_url

    @api.model
    def get_cur(self):
        return self.env.ref('oejia_wx.wx_config_data_1')

    @api.multi
    def name_get(self):
        return [(e.id, u'公众号配置') for e in self]

    @api.model
    def wxenv(self):
        from ..rpc import wx_client
        return wx_client.wxenv(self.env)
