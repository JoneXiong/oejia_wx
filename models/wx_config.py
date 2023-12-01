# -*- coding: utf-8 -*-
import hashlib
import time

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
        result = super(WxConfig, self).write(vals)
        for obj in self:
            self.get_new_entry().init(self.env, from_ui=True, key=obj.appkey)
        return result

    @api.model
    def get_new_entry(self):
        from ..rpc import wx_client
        return wx_client.WxEntry()

    @api.multi
    def _compute_wx_url(self):
        objs = self
        for self in objs:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            self.wx_url = '%s/wx_handler/%s'%(base_url, self.appkey)

    @api.model
    def get_cur(self):
        return self.env.ref('oejia_wx.wx_config_data_1')

    @api.multi
    def name_get(self):
        return [(e.id, u'公众号配置') for e in self]

    @api.model
    def wxenv(self, key=None):
        from ..rpc import wx_client
        env = self.env
        if not key:
            key = self.get_cur().appkey
        if key not in wx_client.WxEnvDict:
            wx_client.WxEntry().init(env, key=key)
        return wx_client.WxEnvDict[key]

    def sync_user(self):
        for obj in self:
            self.env['wx.user'].sync(obj)

    def sync_user_confirm(self):
        return self.env['wx.confirm'].window_confirm('确认同步公众号用户',info="此操作可能需要一定时间，确认同步吗？", method='wx.config|sync_user', ids=self.ids)

    def sync_media(self):
        for obj in self:
            self.env['wx.media'].sync(obj)

    def sync_media_confirm(self):
        return self.env['wx.confirm'].window_confirm('确认同步公众号素材',info="此操作可能需要一定时间，确认同步吗？", method='wx.config|sync_media', ids=self.ids)