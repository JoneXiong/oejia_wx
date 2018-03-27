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
    
    wx_channel = fields.Integer('消息对接渠道', default=1)


    #_defaults = {
    #}
    
    def execute(self, cr, uid, ids, context=None):
        super(wx_config_settings,self).execute(cr, uid, ids, context)
        record = self.browse(cr, uid, ids[0], context=context)
        robot.config["TOKEN"] = record.wx_token
        client.wxclient.appid = record.wx_appid
        client.wxclient.appsecret = record.wx_AppSecret
        # 刷新 AccessToken
        client.wxclient._token = None
        _ = client.wxclient.token
            
    def get_default_wx_AccessToken(self, cr, uid, fields, context=None):
        from openerp.http import request
        httprequest = request.httprequest
        return {
                'wx_AccessToken': client.wxclient._token or '',
                'wx_url':  'http://%s/wx_handler'%httprequest.environ.get('HTTP_HOST', '').split(':')[0]
        }
            
    def get_default_wx_appid(self, cr, uid, fields, context=None):
        Param = self.pool.get("ir.config_parameter")
        return {
                'wx_appid': Param.get_param(cr, uid, 'wx_appid', default='appid_xxxxxxxxxxxxxxx', context=context),
                'wx_AppSecret': Param.get_param(cr, uid, 'wx_AppSecret', default='appsecret_xxxxxxxxxxxxxx', context=context),
                'wx_token': Param.get_param(cr, uid, 'wx_token', default='K5Dtswpte', context=context),
                'wx_channel': int(Param.get_param(cr, uid, 'wx_channel', default=1, context=context)),
                }
    
    def set_wx_appid(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        Param = self.pool.get("ir.config_parameter")
        
        Param.set_param(cr, uid, 'wx_appid', config.wx_appid )
        Param.set_param(cr, uid, 'wx_AppSecret', config.wx_AppSecret )
        Param.set_param(cr, uid, 'wx_token', config.wx_token )
        Param.set_param(cr, uid, 'wx_channel', config.wx_channel )
        

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
    
    Corp_Channel = fields.Integer('消息对接渠道', default=2)
    
    def execute(self, cr, uid, ids, context=None):
        super(wxcorp_config_settings,self).execute(cr, uid, ids, context)
        record = self.browse(cr, uid, ids[0], context=context)
        from ..rpc import corp_client
        from ..controllers import wx_handler
        from wechatpy.enterprise.crypto import WeChatCrypto
        wx_handler.crypto = WeChatCrypto(record.Corp_Token, record.Corp_AESKey, record.Corp_Id)
        corp_client.init_client(record.Corp_Id, record.Corp_Agent_Secret)
        corp_client.init_txl_client(record.Corp_Id, record.Corp_Secret)

    def get_default_Corp_AccessToken(self, cr, uid, fields, context=None):
        from openerp.http import request
        httprequest = request.httprequest
        return {
                'Corp_AccessToken': '',
                'Corp_Url':  'http://%s/corp_handler'%httprequest.environ.get('HTTP_HOST', '').split(':')[0]
        }
            
    def get_default_Corp_Id(self, cr, uid, fields, context=None):
        Param = self.pool.get("ir.config_parameter")
        return {
                'Corp_Id': Param.get_param(cr, uid, 'Corp_Id', default='Corp_Id_xxxxxxxxxxxxxxx', context=context),
                'Corp_Secret': Param.get_param(cr, uid, 'Corp_Secret', default='Corp_Secret_xxxxxxxxxxxxxx', context=context),
                'Corp_Agent': Param.get_param(cr, uid, 'Corp_Agent', default='0', context=context),
                'Corp_Token': Param.get_param(cr, uid, 'Corp_Token', default='NN07w58BUvhuHya', context=context),
                'Corp_AESKey': Param.get_param(cr, uid, 'Corp_AESKey', default='esGH2pMM98SwPMMQpXPG5Y5QawuL67E2aBvNP10V8Gl', context=context),
                'Corp_Channel': int(Param.get_param(cr, uid, 'Corp_Channel', default=2, context=context)),
                }
    
    def set_Corp_Id(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        Param = self.pool.get("ir.config_parameter")
        
        Param.set_param(cr, uid, 'Corp_Id', config.Corp_Id )
        Param.set_param(cr, uid, 'Corp_Secret', config.Corp_Secret )
        Param.set_param(cr, uid, 'Corp_Agent', config.Corp_Agent )
        Param.set_param(cr, uid, 'Corp_Token', config.Corp_Token )
        Param.set_param(cr, uid, 'Corp_AESKey', config.Corp_AESKey )
        Param.set_param(cr, uid, 'Corp_Channel', config.Corp_Channel )
    
    
