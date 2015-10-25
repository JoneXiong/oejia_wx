# coding=utf-8

from openerp import models, fields, api


class wx_config_settings(models.TransientModel):
    _name = 'wx.config.settings'
    _description = u'微信配置'
    #_order = 
    _inherit = 'res.config.settings'

    wx_appid = fields.Char('AppId', )
    wx_AppSecret = fields.Char('AppSecret', )
    wx_AccessToken = fields.Char('当前AccessToken', )
    
    wx_url = fields.Char('URL', )
    wx_token = fields.Char('Token', )


    #_defaults = {
    #}