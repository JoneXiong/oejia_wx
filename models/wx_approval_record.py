# coding=utf-8

from odoo import models, fields, api


class WxApprovalRecord(models.Model):

    _name = 'wx.approval.record'
    _description = u'审批记录'

    _order = 'id'

    #res_model = fields.Char(u'单据记录模型')
    #res_id = fields.Integer(u'单据记录ID')

    agent_id = fields.Char(u'AgentID')
    third_no = fields.Char(u'ThirdNo')
    open_sp_status = fields.Selection(selection=[('0', '待提审'), ('1', '审批中'), ('2', '已通过'), ('3', '已驳回'), ('4', '已取消')], string='审批状态')
    user_name = fields.Char('ApplyUserName')
    user_id = fields.Char('ApplyUserId')
    user_image = fields.Char('ApplyUserImage')
    user_party = fields.Char('ApplyUserParty')
    full_data = fields.Text('Data')
    speech = fields.Char('审批意见')
    step = fields.Integer(u'次序')
    item_status = fields.Selection(selection=[('0', '待提审'), ('1', '审批中'), ('2', '已同意'), ('3', '已驳回'), ('4', '已转审')], string='审批操作')

    user_image_html = fields.Html(compute='_get_user_image', string=u'头像')

    @api.one
    def _get_user_image(self):
        self.user_image_html= '<img src=%s width="50px" height="50px" />'%(self.user_image or '/web/static/src/img/placeholder.png')

    @api.model
    def update_obj_status(self, record, third_no, open_sp_status):
        pass
