# coding=utf-8
import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class WxSendMass(models.Model):

    _name = 'wx.send.mass'
    _description = u'群发'

    wx_media_id = fields.Many2one('wx.media', string='选择素材', required=True, domain=[('media_type', '=', 'news')])
    user_ids = fields.Many2many('wx.user', string='选择用户')
    group_ids = fields.Many2many('wx.user.group', string='选择组')
    is_to_all = fields.Boolean('发给所有用户', default=True)
    send_ignore_reprint = fields.Boolean('被判定为转载时，是否继续群发')
    preview = fields.Boolean('发送预览')
    preview_user_id = fields.Many2one('wx.user', string='预览用户')
    msg_id = fields.Char('消息ID')


    @api.multi
    def mass_send(self):
        from ..rpc import wx_client
        entry = wx_client.WxEntry()
        entry.init(self.env)
        for obj in self:
            res = entry.client.message.send_mass_article(
                None,
                obj.wx_media_id.media_id,
                is_to_all = True,
                preview = False
            )
            _logger.info('>>> mass_send ret: %s', res)
            obj.write({'msg_id': res.get('msg_id')})

    @api.multi
    def preview_send(self):
        from ..rpc import wx_client
        entry = wx_client.WxEntry()
        entry.init(self.env)
        for obj in self:
            res = entry.client.message.send_mass_article(
                obj.preview_user_id.openid,
                obj.wx_media_id.media_id,
                is_to_all = False,
                preview = True
            )
            _logger.info('>>> preview_send ret: %s', res)
