# coding=utf-8

import logging

from openerp import models, fields, api
from ..controllers import client
from openerp.http import request
from openerp.exceptions import ValidationError
from ..rpc import corp_client


_logger = logging.getLogger(__name__)

class wx_user(models.Model):
    _name = 'wx.user'
    _description = u'微信用户'
    #_order = 
    #_inherit = []

    city = fields.Char(u'城市', )
    country = fields.Char(u'国家', )
    group_id = fields.Selection('_get_groups', string=u'所属组', default='0')
    headimgurl = fields.Char(u'头像', )
    nickname = fields.Char(u'昵称', )
    openid = fields.Char(u'用户标志', )
    province = fields.Char(u'省份', )
    sex = fields.Selection([(1,u'男'),(2,u'女')], string=u'性别', )
    subscribe = fields.Boolean(u'关注状态', )
    subscribe_time = fields.Char(u'关注时间', )
    
    headimg= fields.Html(compute='_get_headimg', string=u'头像')

    #_defaults = {
    #}
    
    @api.model
    def sync(self):
        next_openid = 'init'
        c_total = 0
        c_flag = 0
        g_flag = True
        objs = self.env['wx.user.group'].search([])
        group_list = [ e.group_id for e in objs]
        while next_openid:
            if next_openid=='init':next_openid = None
            followers_dict= client.wxclient.get_followers(next_openid)
            c_total = followers_dict['total']
            m_count = followers_dict['count']
            next_openid = followers_dict['next_openid']
            print 'get %s users'%m_count
            if next_openid:
                m_openids = followers_dict['data']['openid']
                for openid in m_openids:
                    c_flag +=1
                    print 'total %s users, now sync the %srd %s .'%(c_total, c_flag, openid)
                    rs = self.search( [('openid', '=', openid)] )
                    if rs.exists():
                        info = client.wxclient.get_user_info(openid)
                        info['group_id'] = str(info['groupid'])
                        if g_flag and info['group_id'] not in group_list:
                            self.env['wx.user.group'].sync()
                            g_flag = False
                        rs.write(info)
                    else:
                        info = client.wxclient.get_user_info(openid)
                        info['group_id'] = str(info['groupid'])
                        if g_flag and info['group_id'] not in group_list:
                            self.env['wx.user.group'].sync()
                            g_flag = False
                        self.create(info)
                
        print 'total:',c_total
        
    @api.one
    def _get_headimg(self):
        self.headimg= '<img src=%s width="100px" height="100px" />'%(self.headimgurl or '/web/static/src/img/placeholder.png')
        
    #@api.one
    def _get_groups(self):
        Group = self.env['wx.user.group']
        objs = Group.search([])
        return [(str(e.group_id), e.group_name) for e in objs]


class wx_user_group(models.Model):
    _name = 'wx.user.group'
    _description = u'微信用户组'
    #_order = 
    #_inherit = []

    count = fields.Integer(u'用户数', )
    group_id = fields.Integer(u'组编号', )
    group_name = fields.Char(u'组名', )
    user_ids = fields.One2many('wx.user', 'group_id', u'用户', )

    #_defaults = {
    #}
    
    @api.model
    def sync(self):
        groups =  client.wxclient.get_groups()
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
            
class wx_corpuser(models.Model):
    _name = 'wx.corpuser'
    _description = u'企业号用户'
    
    name =  fields.Char('昵称', required = True)
    userid = fields.Char('账号', required = True)
    avatar = fields.Char('头像', )
    position = fields.Char('职位', )
    gender = fields.Selection([(1,'男'),(2,'女')], string='性别', )
    weixinid = fields.Char('微信号', )
    mobile = fields.Char('手机号',)
    email = fields.Char('邮箱',)
    status = fields.Selection([(1,'已关注'),(2,'已禁用'),(4,'未关注')], string='状态', default=4)
    extattr = fields.Char('扩展属性', )
    
    avatarimg= fields.Html(compute='_get_avatarimg', string=u'头像')
    
    _sql_constraints = [
        ('userid_key', 'UNIQUE (userid)',  '账号已存在 !'),
        ('weixinid_key', 'UNIQUE (weixinid)',  '微信号已存在 !'),
        ('email_key', 'UNIQUE (email)',  '邮箱已存在 !'),
        ('mobile_key', 'UNIQUE (mobile)',  '手机号已存在 !')
    ]
    
    @api.one
    def _get_avatarimg(self):
        self.avatarimg= '<img src=%s width="100px" height="100px" />'%(self.avatar or '/web/static/src/img/placeholder.png')
        
    @api.model
    def create(self, values):
        _logger.info('wx.corpuser create >>> %s'%str(values))
        if not (values.get('weixinid', '') or  values.get('mobile', '') or values.get('email', '') ):
            raise ValidationError('手机号、邮箱、微信号三者不能同时为空')
        from_subscribe = False
        if '_from_subscribe' in values:
            from_subscribe = True
            values.pop('_from_subscribe')
        obj = super(wx_corpuser, self).create(values)
        if not from_subscribe:
            arg = {}
            for k,v in values.items():
                if v!=False and k in ['mobile', 'email', 'weixinid', 'gender']:
                    arg[k] = v
            arg['department'] = 1
            if 'weixinid' in arg:
                arg['weixin_id'] = arg.pop('weixinid')
            corp_client.client.user.create(values['userid'], values['name'], **arg)
        return obj
    
    @api.multi
    def write(self, values):
        _logger.info('wx.corpuser write >>> %s %s'%( str(self),str(values) ) )
        objs = super(wx_corpuser, self).write(values)
        arg = {}
        for k,v in values.items():
            if v!=False and k in ['mobile', 'email', 'weixinid', 'gender', 'name']:
                arg[k] = v
        for obj in self:
            if not (obj.weixinid or obj.mobile or obj.email):
                raise ValidationError('手机号、邮箱、微信号三者不能同时为空')
            corp_client.client.user.update(obj.userid, **arg)
        return objs
    
    @api.multi
    def unlink(self):
        _logger.info('wx.corpuser unlink >>> %s'%str(self))
        for obj in self:
            try:
                corp_client.client.user.delete(obj.userid)
            except:
                pass
        ret = super(wx_corpuser, self).unlink()
        return ret
        
    @api.model
    def create_from_res_users(self):
        objs = self.env['res.users'].search([])
        for obj in objs:
            _partner = obj.partner_id
            if _partner.mobile or _partner.email:
                flag1 = False
                if _partner.mobile:
                    flag1 = self.search( [ ('mobile', '=', _partner.mobile) ] ).exists()
                flag2 = False
                if _partner.email:
                    flag2 = self.search( [ ('email', '=', _partner.email) ] ).exists()
                flag3 = self.search( [ ('userid', '=', obj.login) ] ).exists()
                if not (flag1 or flag2 or flag3):
                    try:
                        ret = self.create({
                                     'name': obj.name,
                                     'userid': obj.login,
                                     'mobile': _partner.mobile,
                                     'email': _partner.email
                                     })
                        _partner.write({'wxcorp_user_id': ret.id})
                    except:
                        pass
