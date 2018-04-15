# coding=utf-8

from odoo import models, fields, api


class WxUserUUID(models.Model):
    _name = 'wx.user.uuid'

    openid = fields.Char('微信用户ID')
    uuid = fields.Char('会话ID')
