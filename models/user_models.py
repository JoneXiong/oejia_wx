# coding=utf-8

from openerp import models, fields, api


class wx_user(models.Model):
    _name = 'wx.user'
    _description = u'微信用户'
    #_order = 
    #_inherit = []

    city = fields.Char(u'城市', )
    country = fields.Char(u'国家', )
    group_id = fields.Many2one('wx.user.group', u'所属组', )
    headimgurl = fields.Char(u'头像', )
    nickname = fields.Char(u'昵称', )
    openid = fields.Char(u'用户标志', )
    province = fields.Char(u'省份', )
    sex = fields.Selection([('1',u'男'),('2',u'女')], string=u'性别', )
    subscribe = fields.Boolean(u'关注状态', )
    subscribe_time = fields.Char(u'关注时间', )

    #_defaults = {
    #}


class wx_user_group(models.Model):
    _name = 'wx.user.group'
    _description = u'微信用户组'
    #_order = 
    #_inherit = []

    count = fields.Integer(u'用户数', )
    group_id = fields.Char(u'组编号', )
    group_name = fields.Char(u'组名', )
    user_ids = fields.One2many('wx.user', 'group_id', u'用户', )

    #_defaults = {
    #}