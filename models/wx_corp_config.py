# -*- coding: utf-8 -*-

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
    Corp_Agent_Secret = fields.Char('应用 Secret')
    #Corp_AccessToken = fields.Char('当前 AccessToken', readonly=True)

    Corp_Url = fields.Char('URL', readonly=True, compute='_compute_wx_url', help='请将此URL拷贝填到企业微信官方后台，并确保公网能访问该地址')
    Corp_Token = fields.Char('Token', default=generate_token, help='必须为英文或数字，长度为3-32字符, 系统默认自动生成，也可自行修改')
    Corp_AESKey = fields.Char('EncodingAESKey', default='')

    @api.multi
    def write(self, vals):
        result = super(WxCorpConfig, self).write(vals)
        self.get_new_entry().init(self.env, from_ui=True)
        return result

    @api.multi
    def _compute_wx_url(self):
        objs = self
        for self in objs:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            self.Corp_Url = '%s/corp_handler'%base_url

    @api.model
    def get_cur(self):
        return self.env.ref('oejia_wx.wx_corp_config_data_1')

    @api.multi
    def name_get(self):
        return [(e.id, u'企业微信配置') for e in self]

    @api.model
    def corpenv(self):
        from ..rpc import corp_client
        env = self.env
        dbname = env.cr.dbname
        if dbname not in corp_client.CorpEnvDict:
            corp_client.CorpEntry().init(env)
        return corp_client.CorpEnvDict[dbname]

    @api.model
    def get_new_entry(self):
        from ..rpc import corp_client
        return corp_client.CorpEntry()
