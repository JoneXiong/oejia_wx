# -*- coding: utf-8 -*-
import hashlib
import time

from odoo import models, fields, api


class WxAppConfig(models.Model):

    _name = 'wx.app.config'
    _description = u'小程序对接设置'
    _rec_name = 'app_id'

    app_id = fields.Char('AppID')
    secret = fields.Char('Secret')

    token = fields.Char('Token', default=lambda self: self._generate_token())
    aeskey = fields.Char('AESKey')

    handler_url = fields.Char('消息对接URL', readonly=True, compute='_compute_handler_url', help='这里显示当前用于小程序消息对接的接口URL，无需修改，请将其填入小程序后台相应的地方')

    appkey = fields.Char(string='唯一编码', compute='_appkey_compute', store=True, readonly=True, copy=False, index=True)

    _sql_constraints = [
        ('unique_appkey', 'unique (appkey)', '唯一编码不可重复！')
    ]

    @api.depends('create_date')
    def _appkey_compute(self):
        for obj in self:
            obj.appkey = hashlib.md5('wx.corp.config{}{}'.format(obj.id, time.time()).encode('utf-8')).hexdigest()[8:-8][4:-4]

    @api.multi
    def write(self, vals):
        result = super(WxAppConfig, self).write(vals)
        for obj in self:
            self.get_new_entry().init(self.env, from_ui=True, key=obj.appkey)
        return result

    @api.model
    def get_new_entry(self):
        from ..rpc import app_client
        return app_client.AppEntry()

    @api.multi
    def _compute_handler_url(self):
        objs = self
        for self in objs:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            self.handler_url = '%s/app_handler/%s'%(base_url, self.appkey)

    @api.model
    def get_cur(self):
        return self.env.ref('oejia_wx.wx_app_config_data_1')

    @api.multi
    def name_get(self):
        return [(e.id, u'小程序对接设置') for e in self]

    @api.model
    def appenv(self, key=None):
        from ..rpc import app_client
        env = self.env
        if not key:
            key = self.get_cur().appkey
        if key not in app_client.AppEnvDict:
            app_client.AppEntry().init(env, key=key)
        return app_client.AppEnvDict[key]

    def _generate_token(length=''):
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
