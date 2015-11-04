# coding=utf-8

from openerp import models, fields, api
from ..controllers.routes import  robot
from ..controllers import client

class wx_config_settings(models.TransientModel):
    _name = 'wx.config.settings'
    _description = u'微信配置'
    #_order = 
    _inherit = 'res.config.settings'

    wx_appid = fields.Char('AppId', )
    wx_AppSecret = fields.Char('AppSecret', )
    wx_AccessToken = fields.Char('当前AccessToken', readonly=True)
    
    wx_url = fields.Char('URL', readonly=True)
    wx_token = fields.Char('Token', default='K5Dtswpte')


    #_defaults = {
    #}
    
    def execute(self, cr, uid, ids, context=None):
        super(wx_config_settings,self).execute(cr, uid, ids, context)
        record = self.browse(cr, uid, ids[0], context=context)
        robot.config["TOKEN"] = record.wx_token
        client.wxclient.appid = record.wx_appid
        client.wxclient.appsecret = record.wx_AppSecret
            
    def get_default_wx_AccessToken(self, cr, uid, fields, context=None):
        from openerp.http import request
        httprequest = request.httprequest
        return {
                'wx_AccessToken': client.wxclient._token or '',
                'wx_url':  'http://%s/wx_handler'%httprequest.environ.get('HTTP_HOST', '')
        }
            
    def get_default_wx_appid(self, cr, uid, fields, context=None):
        Param = self.pool.get("ir.config_parameter")
        return {
                'wx_appid': Param.get_param(cr, uid, 'wx_appid', default='appid_xxxxxxxxxxxxxxx', context=context),
                'wx_AppSecret': Param.get_param(cr, uid, 'wx_AppSecret', default='appsecret_xxxxxxxxxxxxxx', context=context),
                'wx_token': Param.get_param(cr, uid, 'wx_token', default='token_xxxxxxxx', context=context),
                }
    
    def set_wx_appid(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        Param = self.pool.get("ir.config_parameter")
        
        Param.set_param(cr, uid, 'wx_appid', config.wx_appid )
        Param.set_param(cr, uid, 'wx_AppSecret', config.wx_AppSecret )
        Param.set_param(cr, uid, 'wx_token', config.wx_token )