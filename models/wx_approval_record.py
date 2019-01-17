# coding=utf-8

from odoo import models, fields, api


class WxApprovalRecord(models.Model):

    _name = 'wx.approval.record'
    _description = u'企业微信审批记录'

    _order = 'res_id desc,id'

    res_model = fields.Char(u'单据记录模型')
    res_id = fields.Integer(u'单据记录ID')

    agent_id = fields.Char(u'AgentID')
    third_no = fields.Char(u'ThirdNo')
    open_sp_status = fields.Selection(selection=[('0', '待提审'), ('1', '审批中'), ('2', '已通过'), ('3', '已驳回'), ('4', '已取消')], string='审批状态')
    user_name = fields.Char('ApplyUserName')
    user_id = fields.Char('ApplyUserId')
    user_image = fields.Char('ApplyUserImage')
    user_party = fields.Char('ApplyUserParty')
    full_data = fields.Text('Data')
