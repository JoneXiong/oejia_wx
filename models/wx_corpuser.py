# coding=utf-8

import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

from .. import utils

_logger = logging.getLogger(__name__)


class wx_corpuser(models.Model):
    _name = 'wx.corpuser'
    _description = u'成员'

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
    corp_config_id = fields.Many2one('wx.corp.config','来源')

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
            self.avatarimg= '<img src=%s width="100px" height="100px" />'%(self.avatar or utils.DEFAULT_IMG_URL)

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
                import traceback;traceback.print_exc()
        self.write({'status': '2'})

    def update_local(self):
        for obj in self:
            self.sync_from_remote(obj.corp_config_id, userid=obj.userid)

    @api.model
    def sync_from_remote(self, config, department_id=1, deal_other_info=False, userid=False):
        '''
        从企业微信通讯录同步
        '''
        _logger.info('>>> sync_from_remote %s', config)
        from wechatpy.exceptions import WeChatClientException
        try:
            entry = self.env['wx.corp.config'].corpenv(config.appkey)
            if not config.Corp_Id:
                raise ValidationError(u'尚未做企业微信对接配置')
            #users = entry.txl_client.user.list(department_id, fetch_child=True)
            if userid:
                userid_list = [{'userid': userid}]
            else:
                if not entry.txl_client:
                    raise ValidationError(u'企业微信对接的“通讯录 Secret”配置不正确或未配置')
                userid_list = entry.txl_client.get('user/list_id')['dept_user']
            for userid in userid_list:
                try:
                    info = entry.client.user.get(userid['userid'])
                except:
                    continue
                _logger.info('>>> user get return %s', info)
                if 'DefaultAvatar' in info.get('avatar', ''):
                    info.pop('avatar')
                info['_from_subscribe'] = True
                if 'gender' in info:
                    info['gender'] = str(info['gender'])
                if 'status' in info:
                    info['status'] = str(info['status'])
                rs = self.search( [('userid', '=', info['userid'])] )
                if not rs.exists():
                    info['corp_config_id'] = config.id
                    rs = self.create(info)
                else:
                    rs.write(info)
                if deal_other_info:
                    rs.deal_other_info(info)
        except WeChatClientException as e:
            raise ValidationError(u'微信服务请求异常，异常码: %s 异常信息: %s'%(e.errcode, e.errmsg))
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def deal_other_info(self, info):
        pass

    @api.multi
    def sync_from_remote_confirm(self):
        return self.env['wx.confirm'].window_confirm('确认同步已有企业微信用户至本系统',info="此操作可能需要一定时间，确认同步吗？", method='wx.corpuser|sync_from_remote')

    @api.multi
    def send_text(self, text):
        from wechatpy.exceptions import WeChatClientException
        _logger.info('>>>> send_text to %s %s', self, text)
        for obj in self:
            try:
                entry = self.env['wx.corp.config'].corpenv(obj.corp_config_id.appkey)
                entry.client.message.send_text(entry.current_agent, obj.userid, text)
            except WeChatClientException as e:
                _logger.info(u'微信消息发送失败 %s'%e)
                raise UserError(u'发送失败 %s'%e)

    @api.multi
    def send_text_confirm(self):
        self.ensure_one()
        return self.env['wx.confirm'].window_input_confirm('发送微信消息', 'wx.corpuser|send_text', self.id)
