# coding=utf-8

from odoo import models, fields, api


class WxConfirm(models.TransientModel):

    _name = 'wx.confirm'
    _description = u'确认'

    info = fields.Text("信息")
    model = fields.Char('模型')
    method = fields.Char('方法')

    @api.multi
    def execute(self):
        self.ensure_one()
        active_ids = self._context.get('record_ids')
        rs = self.env[self.model].browse(active_ids)
        ret = getattr(rs, self.method)()
        return ret

    @api.multi
    def execute_with_info(self):
        self.ensure_one()
        active_ids = self._context.get('record_ids')
        rs = self.env[self.model].browse(active_ids)
        ret = getattr(rs, self.method)(self.info)
        return ret
