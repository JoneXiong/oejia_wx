# coding=utf-8

import logging

from openerp import models, fields, api
from ..controllers import client
from openerp.http import request
from openerp.exceptions import ValidationError, UserError


_logger = logging.getLogger(__name__)

class wx_user(models.Model):
    _name = 'wx.user'
    _description = u'公众号用户'
    _rec_name = 'nickname'
    _order = 'id desc'

    city = fields.Char(u'城市', )
    country = fields.Char(u'国家', )
    group_id = fields.Selection('_get_groups', string=u'所属组', default='0')
    headimgurl = fields.Char(u'头像', )
    nickname = fields.Char(u'昵称', )
    openid = fields.Char(u'用户标志', )
    unionid = fields.Char('UnionId')
    province = fields.Char(u'省份', )
    sex = fields.Selection([('0', '未知'), ('1',u'男'),('2',u'女')], string=u'性别', )
    subscribe = fields.Boolean(u'关注状态', )
    subscribe_time = fields.Char(u'关注时间', )
    subscribe_time_show = fields.Char(compute='_get_subscribe_time', string=u'关注时间')

    headimg= fields.Html(compute='_get_headimg', string=u'头像')
    last_uuid = fields.Char('会话ID')
    last_uuid_time = fields.Datetime('会话ID时间')

    def _parse_values(self, values):
        info = values
        if 'groupid' in info:
            info['group_id'] = str(info['groupid'])
        if 'sex' in info:
            info['sex'] = str(info['sex'])
        return info

    @api.multi
    def write(self, values):
        values = self._parse_values(values)
        objs = super(wx_user, self).write(values)
        return objs

    @api.model
    def create(self, values):
        values = self._parse_values(values)
        obj = super(wx_user, self).create(values)
        return obj

    def update_last_uuid(self, uuid):
        self.write({'last_uuid': uuid, 'last_uuid_time': fields.Datetime.now()})
        self.env['wx.user.uuid'].sudo().create({'openid': self.openid, 'uuid': uuid})

    @api.model
    def sync(self):
        from ..controllers import client
        entry = client.wxenv(self.env)
        if not entry.wx_appid:
            raise ValidationError(u'尚未做公众号对接配置')
        next_openid = 'init'
        c_total = 0
        c_flag = 0
        g_flag = True
        objs = self.env['wx.user.group'].search([])
        group_list = [ e.group_id for e in objs]
        while next_openid:
            if next_openid=='init':next_openid = None
            from werobot.client import ClientException
            try:
                followers_dict= entry.wxclient.get_followers(next_openid)
            except ClientException as e:
                raise ValidationError(u'微信服务请求异常，异常信息: %s'%e)
            c_total = followers_dict['total']
            m_count = followers_dict['count']
            next_openid = followers_dict['next_openid']
            _logger.info('get %s users'%m_count)
            if next_openid:
                m_openids = followers_dict['data']['openid']
                for openid in m_openids:
                    c_flag +=1
                    _logger.info('total %s users, now sync the %srd %s .'%(c_total, c_flag, openid))

                    info = entry.wxclient.get_user_info(openid)
                    groupid = info.get('groupid')
                    if g_flag and groupid and groupid not in group_list:
                        self.env['wx.user.group'].sync()
                        g_flag = False
                    rs = self.search( [('openid', '=', openid)] )
                    if rs.exists():
                        rs.write(info)
                    else:
                        self.create(info)

        _logger.info('sync total: %s'%c_total)

    @api.model
    def sync_confirm(self):
        new_context = dict(self._context) or {}
        new_context['default_info'] = "此操作可能需要一定时间，确认同步吗？"
        new_context['default_model'] = 'wx.user'
        new_context['default_method'] = 'sync'
        #new_context['record_ids'] = self.id
        return {
            'name': u'确认同步公众号用户',
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
    def _get_headimg(self):
        objs = self
        for self in objs:
            self.headimg= '<img src=%s width="100px" height="100px" />'%(self.headimgurl or '/web/static/src/img/placeholder.png')

    @api.multi
    def _get_subscribe_time(self):
        import datetime
        objs = self
        for self in objs:
            dt = datetime.datetime.fromtimestamp(int(self.subscribe_time))
            self.subscribe_time_show = dt.strftime("%Y-%m-%d %H:%M:%S")

    def _get_groups(self):
        Group = self.env['wx.user.group']
        objs = Group.search([])
        return [(str(e.group_id), e.group_name) for e in objs] or [('0','默认组')]

    @api.multi
    def send_text(self, text):
        from werobot.client import ClientException
        from ..controllers import client
        entry = client.wxenv(self.env)
        for obj in self:
            try:
                entry.send_text(obj.openid, text)
            except ClientException as e:
                _logger.info(u'微信消息发送失败 %s'%e)
                raise UserError(u'发送失败 %s'%e)

    @api.multi
    def send_text_confirm(self):
        self.ensure_one()

        new_context = dict(self._context) or {}
        new_context['default_model'] = 'wx.user'
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


class wx_user_group(models.Model):
    _name = 'wx.user.group'
    _description = u'公众号用户组'
    _rec_name = 'group_name'

    count = fields.Integer(u'用户数', )
    group_id = fields.Integer(u'组编号', )
    group_name = fields.Char(u'组名', )
    user_ids = fields.One2many('wx.user', 'group_id', u'用户', )


    @api.model
    def sync(self):
        from ..controllers import client
        entry = client.wxenv(self.env)
        if not entry.wx_appid:
            raise ValidationError(u'尚未做公众号对接配置')
        from werobot.client import ClientException
        try:
            groups =  entry.wxclient.get_groups()
        except ClientException as e:
            raise ValidationError(u'微信服务请求异常，异常信息: %s'%e)
        for group in groups['groups']:
            rs = self.search( [('group_id', '=', group['id']) ] )
            if rs.exists():
                rs.write({
                             'group_name': group['name'],
                             'count': group['count'],
                             })
            else:
                self.create({
                             'group_id': str(group['id']),
                             'group_name': group['name'],
                             'count': group['count'],
                             })

    @api.model
    def sync_confirm(self):
        new_context = dict(self._context) or {}
        new_context['default_info'] = "此操作可能需要一定时间，确认同步吗？"
        new_context['default_model'] = 'wx.user.group'
        new_context['default_method'] = 'sync'
        #new_context['record_ids'] = self.id
        return {
            'name': u'确认同步公众号用户组',
            'type': 'ir.actions.act_window',
            'res_model': 'wx.confirm',
            'res_id': None,
            'view_mode': 'form',
            'view_type': 'form',
            'context': new_context,
            'view_id': self.env.ref('oejia_wx.wx_confirm_view_form').id,
            'target': 'new'
        }

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
    def unlink(self):
        _logger.info('wx.corpuser unlink >>> %s'%str(self))
        for obj in self:
            try:
                entry = self.env['wx.corp.config'].corpenv()
                entry.txl_client.user.delete(obj.userid)
            except:
                pass
        ret = super(wx_corpuser, self).unlink()
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
