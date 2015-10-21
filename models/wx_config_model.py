# coding=utf-8

from openerp import models, fields, api


class wx_config_settings(models.Model):
    _name = 'wx.config.settings'
    _description = u'微信配置'
    #_order = 
    _inherit = 'res.config.settings'

    wx_AccessToken = fields.Char('当前AccessToken', )
    wx_AppSecret = fields.Char('AppSecret', )
    
    wx_appid = fields.Char('AppId', )
    wx_token = fields.Char('Token', )
    wx_url = fields.Char('URL', )

    #_defaults = {
    #}