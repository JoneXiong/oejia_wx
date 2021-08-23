# coding=utf-8

import logging

from openerp import models, fields, api
from openerp.exceptions import ValidationError, UserError


_logger = logging.getLogger(__name__)


class wx_corpuser(models.Model):
    _name = 'wx.corpuser'
    _description = u'企业号用户'

    name =  fields.Char('昵称', required = True)
    userid = fields.Char('账号', required = True)
    avatar = fields.Char('头像', )
    position = fields.Char('职位', )
    gender = fields.Selection([('0','未知'), ('1','男'),('2','女')], string='性别', )
    weixinid = fields.Char('微信号', )
    mobile = fields.Char('手机号',)
    email = fields.Char('邮箱',)
    status = fields.Selection([('1','已关注'),('2','已禁用'),('4','未关注'), ('5','退出企业')], string='状态', default='4')
    extattr = fields.Char('扩展属性', )

    avatarimg= fields.Html(compute='_get_avatarimg', string=u'头像')
    last_uuid = fields.Char('会话ID')
    last_uuid_time = fields.Datetime('会话ID时间')

    # department, enable, english_name, hide_mobile, isleader, order, qr_code, telephone
    alias = fields.Char('别名')

    _sql_constraints = [
        ('userid_key', 'UNIQUE (userid)',  '账号已存在 !'),
    ]

    def update_last_uuid(self, uuid):
        self.write({'last_uuid': uuid, 'last_uuid_time': fields.Datetime.now()})
        self.env['wx.corpuser.uuid'].sudo().create({'userid': self.userid, 'uuid': uuid})

    @api.multi
    def _get_avatarimg(self):
        objs = self
        for self in objs:
            self.avatarimg= '<img src=%s width="100px" height="100px" />'%(self.avatar or '/web/static/src/img/placeholder.png')

    @api.model
    def create(self, values):
        _logger.info('wx.corpuser create >>> %s'%str(values))
        values['email'] = values.get('email', False)
        values['mobile'] = values.get('mobile', False)
        if not (values['mobile'] or values['email']) and not '_from_subscribe' in values:
            raise ValidationError('手机号、邮箱不能同时为空')
        from_subscribe = False
        if '_from_subscribe' in values:
            from_subscribe = True
            values.pop('_from_subscribe')
        obj = super(wx_corpuser, self).create(values)
        if not from_subscribe:
            arg = {}
            for k,v in values.items():
                if v!=False and k in ['mobile', 'email', 'weixinid', 'gender']: #'alias'
                    arg[k] = v
            arg['department'] = 1
            if 'weixinid' in arg:
                arg['weixin_id'] = arg.pop('weixinid')
            from wechatpy.exceptions import WeChatClientException
            try:
                entry = self.env['wx.corp.config'].corpenv()
                entry.txl_client.user.create(values['userid'], values['name'], **arg)
            except WeChatClientException as e:
                if e.errcode==60102:
                    _logger.info('>>> corpuser %s exist', values['userid'])
                else:
                    raise ValidationError(u'微信服务请求异常，异常码: %s 异常信息: %s'%(e.errcode, e.errmsg))
        return obj

    @api.multi
    def write(self, values):
        _logger.info('wx.corpuser write >>> %s %s'%( str(self),str(values) ) )
        from_subscribe = False
        if '_from_subscribe' in values:
            from_subscribe = True
            values.pop('_from_subscribe')
        objs = super(wx_corpuser, self).write(values)
        if from_subscribe:
            return objs
        arg = {}
        for k,v in values.items():
            if v!=False and k in ['mobile', 'email', 'weixinid', 'gender', 'name']: #'alias'
                arg[k] = v
        for obj in self:
            if not (obj.mobile or obj.email) and ('mobile' in values or 'email' in values):
                raise ValidationError('手机号、邮箱不能同时为空')
            if not arg:
                continue
            from wechatpy.exceptions import WeChatClientException
            try:
                entry = self.env['wx.corp.config'].corpenv()
                entry.txl_client.user.update(obj.userid, **arg)
            except WeChatClientException as e:
                raise ValidationError(u'微信服务请求异常，异常码: %s 异常信息: %s'%(e.errcode, e.errmsg))
        return objs

    @api.multi
    def delete_corpuser(self):
        _logger.info('wx.corpuser delete_corpuser >>> %s'%str(self))
        for obj in self:
            try:
                entry = self.env['wx.corp.config'].corpenv()
                entry.txl_client.user.delete(obj.userid)
            except:
                pass
        self.write({'status': '4'})
        return ret

    @api.model
    def sync_from_remote(self, department_id=1):
        '''
        从企业微信通讯录同步
        '''
        from wechatpy.exceptions import WeChatClientException
        try:
            entry = self.env['wx.corp.config'].corpenv()
            config = self.env['wx.corp.config'].sudo().get_cur()
            if not config.Corp_Id:
                raise ValidationError(u'尚未做企业微信对接配置')
            users = entry.txl_client.user.list(department_id, fetch_child=True)
            for info in users:
                info['_from_subscribe'] = True
                info['gender'] = str(info['gender'])
                if 'status' in info:
                    info['status'] = str(info['status'])
                rs = self.search( [('userid', '=', info['userid'])] )
                if not rs.exists():
                    self.create(info)
                else:
                    rs.write(info)
        except WeChatClientException as e:
            raise ValidationError(u'微信服务请求异常，异常码: %s 异常信息: %s'%(e.errcode, e.errmsg))

    @api.multi
    def sync_from_remote_confirm(self):
        new_context = dict(self._context) or {}
        new_context['default_info'] = "此操作可能需要一定时间，确认同步吗？"
        new_context['default_model'] = 'wx.corpuser'
        new_context['default_method'] = 'sync_from_remote'
        return {
            'name': u'确认同步已有企业微信用户至本系统',
            'type': 'ir.actions.act_window',
            'res_model': 'wx.confirm',
            'res_id': None,
            'view_mode': 'form',
            'view_type': 'form',
            'context': new_context,
            'view_id': self.env.ref('oejia_wx.wx_confirm_view_form').id,
            'target': 'new'
        }

    @api.multi
    def send_text(self, text):
        from wechatpy.exceptions import WeChatClientException
        Param = self.env['ir.config_parameter'].sudo()
        for obj in self:
            try:
                entry = self.env['wx.corp.config'].corpenv()
                entry.client.message.send_text(entry.current_agent, obj.userid, text)
            except WeChatClientException as e:
                _logger.info(u'微信消息发送失败 %s'%e)
                raise UserError(u'发送失败 %s'%e)

    @api.multi
    def send_text_confirm(self):
        self.ensure_one()

        new_context = dict(self._context) or {}
        new_context['default_model'] = 'wx.corpuser'
        new_context['default_method'] = 'send_text'
        new_context['record_ids'] = self.id
        return {
            'name': u'发送微信消息',
            'type': 'ir.actions.act_window',
            'res_model': 'wx.confirm',
            'res_id': None,
            'view_mode': 'form',
            'view_type': 'form',
            'context': new_context,
            'view_id': self.env.ref('oejia_wx.wx_confirm_view_form_send').id,
            'target': 'new'
        }
