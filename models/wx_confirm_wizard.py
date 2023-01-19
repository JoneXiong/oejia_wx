# coding=utf-8
import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)

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
        if self.method:
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

    def window_confirm(self, title, info=None, method=None, ids=None, view_id=None):
        new_context = dict(self._context) or {}
        new_context['default_info'] = info or ''
        if method:
            _model, _method = method.split('|')
            new_context['default_model'] = _model
            new_context['default_method'] = _method
        else:
            new_context['default_model'] = False
            new_context['default_method'] = False
        if ids:
            new_context['record_ids'] = ids
        return {
            'name': title,
            'type': 'ir.actions.act_window',
            'res_model': 'wx.confirm',
            'res_id': None,
            'view_mode': 'form',
            'view_type': 'form',
            'context': new_context,
            'view_id': view_id or self.env.ref('oejia_wx.wx_confirm_view_form').id,
            'target': 'new'
        }

    def window_input_confirm(self, title, method, ids=None, view_id=None):
        new_context = dict(self._context) or {}
        _model, _method = method.split('|')
        new_context['default_model'] = _model
        new_context['default_method'] = _method
        new_context['record_ids'] = ids
        return {
            'name': title,
            'type': 'ir.actions.act_window',
            'res_model': 'wx.confirm',
            'res_id': None,
            'view_mode': 'form',
            'view_type': 'form',
            'context': new_context,
            'view_id': view_id or self.env.ref('oejia_wx.wx_confirm_view_form_send').id,
            'target': 'new'
        }
