# coding=utf-8

from odoo import models, fields, api


class CorpuserUUID(models.Model):
    _name = 'wx.corpuser.uuid'
    _description = u'企业微信会话记录'

    userid = fields.Char('微信用户ID')
    uuid = fields.Char('会话ID')

    @api.model
    def refresh(self):
        pass
