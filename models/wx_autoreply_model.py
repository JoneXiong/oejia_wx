# coding=utf-8

from openerp import models, fields, api

from .menu_about_models import ACTION_OPTION


class wx_autoreply(models.Model):
    _name = 'wx.autoreply'
    _description = u'自动回复'
    _rec_name = 'key'
    #_order = 
    #_inherit = []

    key = fields.Char('匹配内容', )
    type = fields.Selection( [(1,'完全匹配'),(2,'模糊匹配'),(3,'正则匹配')], '匹配方式', )
    action = fields.Reference(string='动作', selection=ACTION_OPTION)
    sequence = fields.Integer('匹配顺序', help="数字越小越先匹配")

    _defaults = {
                 'type': 1,
                 'sequence': 0
    }
    _order = 'sequence'
