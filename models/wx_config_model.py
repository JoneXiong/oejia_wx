# coding=utf-8

from openerp import models, fields, api
from ..controllers.routes import  robot
from ..controllers.client import wxclient

class wx_config_settings(models.TransientModel):
    _name = 'wx.config.settings'
    _description = u'微信配置'
    #_order = 
    _inherit = 'res.config.settings'

    wx_appid = fields.Char('AppId', )
    wx_AppSecret = fields.Char('AppSecret', )
    wx_AccessToken = fields.Char('当前AccessToken', )
    
    wx_url = fields.Char('URL', )
    wx_token = fields.Char('Token', default='K5Dtswpte')


    #_defaults = {
    #}
    
    def execute(self, cr, uid, ids, context=None):
        super(wx_config_settings,self).execute(cr, uid, ids, context)
        for record in self.browse(cr, uid, ids, context=context):
            robot.config["TOKEN"] = record.wx_token
            wxclient.appid = record.wx_appid
            wxclient.appsecret = record.wx_AppSecret
            