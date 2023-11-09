# -*- coding: utf-8 -*-
import hashlib
import time

from odoo import models, fields, api


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

class WxCorpConfig(models.Model):

    _name = 'wx.corp.config'
    _description = u'对接企业号配置'

    Corp_Id = fields.Char('企业ID', )
    Corp_Secret = fields.Char('通讯录 Secret')
    Corp_Agent = fields.Char('应用 AgentID', default='0')
    Corp_Agent_Name = fields.Char('自建应用名称')
    Corp_Agent_Secret = fields.Char('应用 Secret')
    #Corp_AccessToken = fields.Char('当前 AccessToken', readonly=True)

    Corp_Url = fields.Char('URL', readonly=True, compute='_compute_wx_url', help='请将此URL拷贝填到企业微信官方后台，并确保公网能访问该地址')
    Corp_Token = fields.Char('Token', default=generate_token, help='必须为英文或数字，长度为3-32字符, 系统默认自动生成，也可自行修改')
    Corp_AESKey = fields.Char('EncodingAESKey', default='')
    appkey = fields.Char(string='唯一编码', compute='_appkey_compute', store=True, readonly=True, copy=False, index=True)

    _sql_constraints = [
        ('unique_appkey', 'unique (appkey)', '唯一编码不可重复！')
    ]

    @api.depends('create_date')
    def _appkey_compute(self):
        for obj in self:
            obj.appkey = hashlib.md5('wx.corp.config{}{}'.format(obj.id, time.time()).encode('utf-8')).hexdigest()[8:-8][4:-4]

    def sync_from_remote_confirm(self):
        return self.env['wx.confirm'].window_confirm('确认同步已有企业微信用户至本系统',info="此操作可能需要一定时间，确认同步吗？", method='wx.corp.config|sync_from_remote', ids=self.ids)

    def sync_from_remote(self):
        for obj in self:
            self.env['wx.corpuser'].sync_from_remote(obj)

    @api.multi
    def write(self, vals):
        result = super(WxCorpConfig, self).write(vals)
        for obj in self:
            key = obj.appkey #self.env.cr.dbname
            self.get_new_entry().init(self.env, from_ui=True, key=key)
        return result

    @api.multi
    def _compute_wx_url(self):
        objs = self
        for self in objs:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            self.Corp_Url = '%s/corp_handler/%s'%(base_url, self.appkey)

    @api.model
    def get_cur(self):
        return self.env.ref('oejia_wx.wx_corp_config_data_1').sudo()

    @api.multi
    def name_get(self):
        return [(e.id, u'%s(%s)'%(e.Corp_Agent_Name or '企业微信配置', e.appkey)) for e in self]

    @api.model
    def corpenv(self, key=None):
        from ..rpc import corp_client
        env = self.env
        if not key:
            key = self.get_cur().appkey
        if key not in corp_client.CorpEnvDict:
            corp_client.CorpEntry().init(env, key=key)
        return corp_client.CorpEnvDict[key]

    @api.model
    def get_new_entry(self):
        from ..rpc import corp_client
        return corp_client.CorpEntry()
