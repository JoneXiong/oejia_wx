# coding=utf-8

from openerp import models, fields, api


class res_partner(models.Model):
    _inherit = 'res.partner'
    
    wxcorp_user_id = fields.Many2one('wx.corpuser','关联企业号用户')
