# coding=utf-8

from odoo import models, fields, api
from ..controllers import client

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

class wx_config_settings(models.TransientModel):
    _name = 'wx.config.settings'
    _description = u'对接公众号配置'
    #_order = 
    _inherit = 'res.config.settings'

    wx_appid = fields.Char('AppId', )
    wx_AppSecret = fields.Char('AppSecret', )
    wx_AccessToken = fields.Char('当前AccessToken', readonly=True)

    wx_url = fields.Char('URL', readonly=True, help='请将此URL拷贝填到公众号官方后台，并确保公网能访问该地址')
    wx_token = fields.Char('Token', help='必须为英文或数字，长度为3-32字符, 系统默认自动生成，也可自行修改')



    #_defaults = {
    #}

    @api.multi
    def execute(self):
        self.ensure_one()
        if self.env.user.has_group('oejia_wx.group_wx_conf'):
            self = self.sudo()
        super(wx_config_settings,self).execute()
        from ..controllers import client
        client.WxEntry().init(self.env, from_ui=True)

    @api.model
    def get_default_wx_AccessToken(self, fields):
        from ..controllers import client
        entry = client.wxenv(self.env)
        client = entry
        Param = self.env["ir.config_parameter"]
        return {
                'wx_AccessToken': client.wxclient._token or '',
                'wx_url':  '%s/wx_handler'%Param.get_param('web.base.url')
        }

    @api.model
    def get_default_wx_appid(self, fields):
        Param = self.env["ir.config_parameter"].sudo()
        return {
                'wx_appid': Param.get_param('wx_appid', default=''),
                'wx_AppSecret': Param.get_param('wx_AppSecret', default=''),
                'wx_token': Param.get_param('wx_token', default='K5Dtswpte'),
                }

    @api.multi
    def set_wx_appid(self):
        self.ensure_one()
        config = self
        Param = self.env["ir.config_parameter"].sudo()

        Param.set_param('wx_appid', config.wx_appid )
        Param.set_param('wx_AppSecret', config.wx_AppSecret )
        Param.set_param('wx_token', config.wx_token )

    @api.multi
    def set_values(self):
        if not hasattr(super(wx_config_settings, self), 'set_values'):
            return

        self.ensure_one()
        super(wx_config_settings, self).set_values()
        config = self
        Param = self.env["ir.config_parameter"].sudo()

        Param.set_param('wx_appid', config.wx_appid )
        Param.set_param('wx_AppSecret', config.wx_AppSecret )
        Param.set_param('wx_token', config.wx_token )

    @api.model
    def get_values(self):
        res = super(wx_config_settings, self).get_values()
        Param = self.env["ir.config_parameter"].sudo()

        from ..controllers import client
        entry = client.wxenv(self.env)
        client = entry

        res.update(
            wx_appid = Param.get_param('wx_appid', default=''),
            wx_AppSecret = Param.get_param('wx_AppSecret', default=''),
            wx_token = Param.get_param('wx_token', default=generate_token()),
            wx_AccessToken = client.wxclient._token or '',
            wx_url = '%s/wx_handler'%Param.get_param('web.base.url')
        )
        return res

class wxcorp_config_settings(models.TransientModel):
    _name = 'wx.config.corpsettings'
    _description = u'对接企业号配置'
    _inherit = 'res.config.settings'

    Corp_Id = fields.Char('企业ID', )
    Corp_Secret = fields.Char('通讯录 Secret')
    Corp_Agent = fields.Char('应用 AgentID', default='0')
    Corp_Agent_Secret = fields.Char('Agent Secret')
    #Corp_AccessToken = fields.Char('当前 AccessToken', readonly=True)

    Corp_Url = fields.Char('URL', readonly=True)
    Corp_Token = fields.Char('Token')
    Corp_AESKey = fields.Char('EncodingAESKey', default='')


    @api.multi
    def execute(self):
        self.ensure_one()
        if self.env.user.has_group('oejia_wx.group_wx_conf'):
            self = self.sudo()
        super(wxcorp_config_settings,self).execute()
        from ..rpc import corp_client
        corp_client.CorpEntry().init(self.env, from_ui=True)

    @api.model
    def get_default_Corp_Url(self, fields):
        Param = self.env["ir.config_parameter"]
        return {
                #'Corp_AccessToken': '',
                'Corp_Url':  '%s/corp_handler'%Param.get_param('web.base.url')
        }

    @api.model
    def get_default_Corp_Id(self, fields):
        Param = self.env["ir.config_parameter"].sudo()
        return {
                'Corp_Id': Param.get_param('Corp_Id', default=''),
                'Corp_Secret': Param.get_param('Corp_Secret', default=''),
                'Corp_Agent_Secret': Param.get_param('Corp_Agent_Secret', default=''),
                'Corp_Agent': Param.get_param('Corp_Agent', default='0'),
                'Corp_Token': Param.get_param('Corp_Token', default=''),
                'Corp_AESKey': Param.get_param('Corp_AESKey', default=''),
                }

    @api.multi
    def set_Corp_Id(self):
        self.ensure_one()
        config = self
        Param = self.env["ir.config_parameter"].sudo()

        Param.set_param('Corp_Id', config.Corp_Id )
        Param.set_param('Corp_Secret', config.Corp_Secret )
        Param.set_param('Corp_Agent_Secret', config.Corp_Agent_Secret )
        Param.set_param('Corp_Agent', config.Corp_Agent )
        Param.set_param('Corp_Token', config.Corp_Token )
        Param.set_param('Corp_AESKey', config.Corp_AESKey )

    @api.multi
    def set_values(self):
        if not hasattr(super(wxcorp_config_settings, self), 'set_values'):
            return

        self.ensure_one()
        super(wxcorp_config_settings, self).set_values()
        config = self
        Param = self.env["ir.config_parameter"].sudo()

        Param.set_param('Corp_Id', config.Corp_Id )
        Param.set_param('Corp_Secret', config.Corp_Secret )
        Param.set_param('Corp_Agent_Secret', config.Corp_Agent_Secret )
        Param.set_param('Corp_Agent', config.Corp_Agent )
        Param.set_param('Corp_Token', config.Corp_Token )
        Param.set_param('Corp_AESKey', config.Corp_AESKey )

    @api.model
    def get_values(self):
        res = super(wxcorp_config_settings, self).get_values()
        Param = self.env["ir.config_parameter"].sudo()

        res.update(
            Corp_Id = Param.get_param('Corp_Id', default=''),
            Corp_Secret = Param.get_param('Corp_Secret', default=''),
            Corp_Agent_Secret = Param.get_param('Corp_Agent_Secret', default=''),
            Corp_Agent = Param.get_param('Corp_Agent', default=''),
            Corp_Token = Param.get_param('Corp_Token', default=generate_token()),
            Corp_AESKey = Param.get_param('Corp_AESKey', default=''),
            Corp_Url = '%s/corp_handler'%Param.get_param('web.base.url')
        )
        return res


