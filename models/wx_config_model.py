# coding=utf-8

from openerp import models, fields, api
from ..controllers import client

class wx_config_settings(models.TransientModel):
    _name = 'wx.config.settings'
    _description = u'对接公众号配置'
    #_order = 
    _inherit = 'res.config.settings'

    wx_appid = fields.Char('AppId', )
    wx_AppSecret = fields.Char('AppSecret', )
    wx_AccessToken = fields.Char('当前AccessToken', readonly=True)

    wx_url = fields.Char('URL', readonly=True)
    wx_token = fields.Char('Token', default='K5Dtswpte')



    #_defaults = {
    #}

    @api.multi
    def execute(self):
        self.ensure_one()
        if self.env.user.has_group('oejia_wx.group_wx_conf'):
            self = self.sudo()
        super(wx_config_settings,self).execute()
        from ..controllers import client
        client.WxEntry().init(self.env)

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
            wx_token = Param.get_param('wx_token', default=''),
            wx_AccessToken = client.wxclient._token or '',
            wx_url = '%s/wx_handler'%Param.get_param('web.base.url')
        )
        return res

class wxcorp_config_settings(models.TransientModel):
    _name = 'wx.config.corpsettings'
    _description = u'对接企业号配置'
    _inherit = 'res.config.settings'

    Corp_Id = fields.Char('CorpID', )
    Corp_Secret = fields.Char('通讯录 Secret')
    Corp_Agent = fields.Char('应用 AgentID', default='0')
    Corp_Agent_Secret = fields.Char('Agent Secret')
    #Corp_AccessToken = fields.Char('当前 AccessToken', readonly=True)

    Corp_Url = fields.Char('Corp_Url', readonly=True)
    Corp_Token = fields.Char('Corp_Token', default='NN07w58BUvhuHya')
    Corp_AESKey = fields.Char('Corp_AESKey', default='esGH2pMM98SwPMMQpXPG5Y5QawuL67E2aBvNP10V8Gl')


    @api.multi
    def execute(self):
        self.ensure_one()
        if self.env.user.has_group('oejia_wx.group_wx_conf'):
            self = self.sudo()
        super(wxcorp_config_settings,self).execute()
        from ..rpc import corp_client
        corp_client.CorpEntry().init(self.env)

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
                'Corp_Id': Param.get_param('Corp_Id', default='Corp_Id_xxxxxxxxxxxxxxx'),
                'Corp_Secret': Param.get_param('Corp_Secret', default='Corp_Secret_xxxxxxxxxxxxxx'),
                'Corp_Agent_Secret': Param.get_param('Corp_Agent_Secret', default='Agent_Secret_xxxxxxxxxxxxxx'),
                'Corp_Agent': Param.get_param('Corp_Agent', default='0'),
                'Corp_Token': Param.get_param('Corp_Token', default='NN07w58BUvhuHya'),
                'Corp_AESKey': Param.get_param('Corp_AESKey', default='esGH2pMM98SwPMMQpXPG5Y5QawuL67E2aBvNP10V8Gl'),
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
            Corp_Id = Param.get_param('Corp_Id', default='Corp_Id_xxxxxxxxxxxxxxx'),
            Corp_Secret = Param.get_param('Corp_Secret', default='Corp_Secret_xxxxxxxxxxxxxx'),
            Corp_Agent_Secret = Param.get_param('Corp_Agent_Secret', default='Agent_Secret_xxxxxxxxxxxxxx'),
            Corp_Agent = Param.get_param('Corp_Agent', default='0'),
            Corp_Token = Param.get_param('Corp_Token', default='NN07w58BUvhuHya'),
            Corp_AESKey = Param.get_param('Corp_AESKey', default='esGH2pMM98SwPMMQpXPG5Y5QawuL67E2aBvNP10V8Gl'),
            Corp_Url = '%s/corp_handler'%Param.get_param('web.base.url')
        )
        return res


