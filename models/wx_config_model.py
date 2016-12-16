# coding=utf-8

from openerp import models, fields, api
from ..controllers.routes import  robot
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

    wx_channel = fields.Integer('消息对接渠道', default=0)


    #_defaults = {
    #}

    @api.multi
    def execute(self):
        self.ensure_one()
        super(wx_config_settings,self).execute()
        robot.config["TOKEN"] = self.wx_token
        client.wxclient.appid = self.wx_appid
        client.wxclient.appsecret = self.wx_AppSecret
        # 刷新 AccessToken
        client.wxclient._token = None
        _ = client.wxclient.token

    @api.model
    def get_default_wx_AccessToken(self, fields):
        from openerp.http import request
        httprequest = request.httprequest
        return {
                'wx_AccessToken': client.wxclient._token or '',
                'wx_url':  'http://%s/wx_handler'%httprequest.environ.get('HTTP_HOST', '').split(':')[0]
        }

    @api.model
    def get_default_wx_appid(self, fields):
        Param = self.env["ir.config_parameter"]
        return {
                'wx_appid': Param.get_param('wx_appid', default='appid_xxxxxxxxxxxxxxx'),
                'wx_AppSecret': Param.get_param('wx_AppSecret', default='appsecret_xxxxxxxxxxxxxx'),
                'wx_token': Param.get_param('wx_token', default='K5Dtswpte'),
                'wx_channel': int(Param.get_param('wx_channel', default=0)),
                }

    @api.multi
    def set_wx_appid(self):
        self.ensure_one()
        config = self
        Param = self.env["ir.config_parameter"]

        Param.set_param('wx_appid', config.wx_appid )
        Param.set_param('wx_AppSecret', config.wx_AppSecret )
        Param.set_param('wx_token', config.wx_token )
        Param.set_param('wx_channel', config.wx_channel )


class wxcorp_config_settings(models.TransientModel):
    _name = 'wx.config.corpsettings'
    _description = u'对接企业号配置'
    _inherit = 'res.config.settings'

    Corp_Id = fields.Char('Corp Id', )
    Corp_Secret = fields.Char('Corp Secret', )
    Corp_Agent = fields.Char('Corp Agent ID', default='0')
    Corp_AccessToken = fields.Char('当前Corp_AccessToken', readonly=True)

    Corp_Url = fields.Char('Corp_Url', readonly=True)
    Corp_Token = fields.Char('Corp_Token', default='NN07w58BUvhuHya')
    Corp_AESKey = fields.Char('Corp_AESKey', default='esGH2pMM98SwPMMQpXPG5Y5QawuL67E2aBvNP10V8Gl')

    Corp_Channel = fields.Integer('消息对接渠道', default=0)

    @api.multi
    def execute(self):
        self.ensure_one()
        super(wxcorp_config_settings,self).execute()
        record = self
        from ..rpc import corp_client
        from ..controllers import wx_handler
        from wechatpy.enterprise.crypto import WeChatCrypto
        wx_handler.crypto = WeChatCrypto(record.Corp_Token, record.Corp_AESKey, record.Corp_Id)
        corp_client.init_client(record.Corp_Id, record.Corp_Secret)

    @api.model
    def get_default_Corp_AccessToken(self, fields):
        from openerp.http import request
        httprequest = request.httprequest
        return {
                'Corp_AccessToken': '',
                'Corp_Url':  'http://%s/corp_handler'%httprequest.environ.get('HTTP_HOST', '').split(':')[0]
        }

    @api.model
    def get_default_Corp_Id(self, fields):
        Param = self.env["ir.config_parameter"]
        return {
                'Corp_Id': Param.get_param('Corp_Id', default='Corp_Id_xxxxxxxxxxxxxxx'),
                'Corp_Secret': Param.get_param('Corp_Secret', default='Corp_Secret_xxxxxxxxxxxxxx'),
                'Corp_Agent': Param.get_param('Corp_Agent', default='0'),
                'Corp_Token': Param.get_param('Corp_Token', default='NN07w58BUvhuHya'),
                'Corp_AESKey': Param.get_param('Corp_AESKey', default='esGH2pMM98SwPMMQpXPG5Y5QawuL67E2aBvNP10V8Gl'),
                'Corp_Channel': int(Param.get_param('Corp_Channel', default=0)),
                }

    @api.multi
    def set_Corp_Id(self):
        self.ensure_one()
        config = self
        Param = self.env["ir.config_parameter"]

        Param.set_param('Corp_Id', config.Corp_Id )
        Param.set_param('Corp_Secret', config.Corp_Secret )
        Param.set_param('Corp_Agent', config.Corp_Agent )
        Param.set_param('Corp_Token', config.Corp_Token )
        Param.set_param('Corp_AESKey', config.Corp_AESKey )
        Param.set_param('Corp_Channel', config.Corp_Channel )


