# coding=utf-8

import logging

from openerp import models, fields, api
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
    subscribe_time = fields.Char(u'Subscribe Time', )
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

