# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
from openerp.osv import orm
from openerp import models

class wx_action_act_article(osv.osv):
    _name = 'wx.action.act_article'
    _description = u'返回图文动作'
    #_order = 
    #_inherit = []
    _columns = {
        #'articlesreply_id': fields.many2one('wx.articlesreply', u'图文回复', ),
        'article_ids': fields.one2many('wx.articlesreply.article', 'articles_id', u'内容列表', ),
        'name': fields.char(u'名称', ),
    }
    #_defaults = {
    #}


class wx_action_act_custom(osv.osv):
    _name = 'wx.action.act_custom'
    _description = u'自定义动作'
    #_order = 
    #_inherit = []
    _columns = {
        'excute_content': fields.text(u'执行内容', ),
        'excute_type': fields.selection([('python','Python')],u'执行方式', ),
        'name': fields.char(u'名称', ),
    }
    #_defaults = {
    #}


class wx_action_act_text(osv.osv):
    _name = 'wx.action.act_text'
    _description = u'返回文本动作'
    #_order = 
    #_inherit = []
    _columns = {
        'content': fields.text(u'内容', ),
        'name': fields.char(u'名称', ),
    }
    #_defaults = {
    #}


class wx_action_act_url(osv.osv):
    _name = 'wx.action.act_url'
    _description = u'超链接动作'
    #_order = 
    #_inherit = []
    _columns = {
        'name': fields.char(u'名称', ),
        'url': fields.char(u'链接地址', ),
    }
    #_defaults = {
    #}


#class wx_articlesreply(osv.osv):
#    _name = 'wx.articlesreply'
#    _description = u'图文回复'
#    #_order = 
#    #_inherit = []
#    _columns = {
#        'article_ids': fields.one2many('wx.articlesreply.article', 'articles_id', u'内容列表', ),
#        'name': fields.char(u'名称', ),
#    }
#    #_defaults = {
#    #}


class wx_articlesreply_article(osv.osv):
    _name = 'wx.articlesreply.article'
    _description = u'图文'
    _rec_name = 'title'
    #_order = 
    #_inherit = []
    _columns = {
        'articles_id': fields.many2one('wx.articlesreply', u'所属图文回复', ),
        'description': fields.char(u'描述', required = True, ),
        'img': fields.char(u'图片地址', required = True, ),
        'title': fields.char(u'标题', required = True, ),
        'url': fields.char(u'跳转链接', required = True, ),
    }
    #_defaults = {
    #}


class wx_autoreply(osv.osv):
    
    def _action(self, cursor, user, ids, name, arg, context=None):
        res = {}
        ir_values_obj = self.pool.get('ir.values')
        value_ids = ir_values_obj.search(cursor, user, [
            ('model', '=', self._name), ('key', '=', 'action'),
            ('key2', '=', 'wx_auto_reply'), ('res_id', 'in', ids)],
            context=context)
        values_action = {}
        for value in ir_values_obj.browse(cursor, user, value_ids, context=context):
            values_action[value.res_id] = value.value
        for menu_id in ids:
            res[menu_id] = values_action.get(menu_id, False)
        return res

    def _action_inv(self, cursor, user, menu_id, name, value, arg, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        if self.CONCURRENCY_CHECK_FIELD in ctx:
            del ctx[self.CONCURRENCY_CHECK_FIELD]
        ir_values_obj = self.pool.get('ir.values')
        values_ids = ir_values_obj.search(cursor, user, [
            ('model', '=', self._name), ('key', '=', 'action'),
            ('key2', '=', 'wx_auto_reply'), ('res_id', '=', menu_id)],
            context=context)
        if value and values_ids:
            ir_values_obj.write(cursor, user, values_ids, {'value': value}, context=ctx)
        elif value:
            # no values_ids, create binding
            ir_values_obj.create(cursor, user, {
                'name': u'wx_autoreply_ir_values',
                'model': self._name,
                'value': value,
                'key': 'action',
                'key2': 'wx_auto_reply',
                'res_id': menu_id,
                }, context=ctx)
        elif values_ids:
            # value is False, remove existing binding
            ir_values_obj.unlink(cursor, user, values_ids, context=ctx)

    
    _name = 'wx.autoreply'
    _description = u'自动回复'
    #_order = 
    #_inherit = []
    _columns = {
        'key': fields.char(u'匹配内容', ),
        'type': fields.selection([(1,u'完全匹配'),(2,u'模糊匹配'),(3,u'正则匹配')],u'匹配方式', ),
        'action': fields.function(_action, fnct_inv=_action_inv,
            type='reference', string=u'动作',
            selection=[
                ('wx.action.act_article', u'图文响应'),
                ('wx.action.act_text', u'文本响应'),
                ('wx.action.act_custom', u'自定义动作'),
            ]),
    }
    _defaults = {
                 'type': 1
    }


class wx_config_settings(osv.osv):
    _name = 'wx.config.settings'
    _description = u'微信配置'
    #_order = 
    _inherit = 'res.config.settings'
    _columns = {
        'wx_AccessToken': fields.char(u'当前AccessToken', ),
        'wx_AppSecret': fields.char(u'AppSecret', ),
        'wx_appid': fields.char(u'AppId', ),
        'wx_token': fields.char(u'Token', ),
        'wx_url': fields.char(u'URL', ),
    }
    #_defaults = {
    #}
    
class menu_item_left(orm.Model):
    _name = 'wx.menu.item.left'
    _description = '左菜单项'
    _columns = {
                'menu_id' : fields.many2one('wx.menu', '所属微信菜单', required=True, ondelete='cascade'),
                'sequence' : fields.integer('Sequence', help="sequence"),
                'name': fields.char('名称', ),
                'action': fields.reference('动作', selection=[
                    ('wx.action.act_article', u'图文响应'),
                    ('wx.action.act_text', u'文本响应'),
                    ('wx.action.act_url', u'超链接'),
                    ('wx.action.act_custom', u'自定义动作'),
                 ])
                }
    
    _order = 'sequence'
    
class menu_item_middle(orm.Model):
    _name = 'wx.menu.item.middle'
    _description = '中菜单项'
    _columns = {
                'menu_id' : fields.many2one('wx.menu', '所属微信菜单', required=True, ondelete='cascade'),
                'sequence' : fields.integer('Sequence', help="sequence"),
                'name': fields.char('名称', ),
                'action': fields.reference('动作', selection=[
                    ('wx.action.act_article', u'图文响应'),
                    ('wx.action.act_text', u'文本响应'),
                    ('wx.action.act_url', u'超链接'),
                    ('wx.action.act_custom', u'自定义动作'),
                 ])
                }
    
    _order = 'sequence'
    
class menu_item_right(orm.Model):
    _name = 'wx.menu.item.right'
    _description = '右菜单项'
    _columns = {
                'menu_id' : fields.many2one('wx.menu', '所属微信菜单', required=True, ondelete='cascade'),
                'sequence' : fields.integer('Sequence', help="sequence"),
                'name': fields.char('名称', ),
                'action': fields.reference('动作', selection=[
                    ('wx.action.act_article', u'图文响应'),
                    ('wx.action.act_text', u'文本响应'),
                    ('wx.action.act_url', u'超链接'),
                    ('wx.action.act_custom', u'自定义动作'),
                 ])
                }
    
    _order = 'sequence'

class wx_menu(osv.osv):
    
    def _action(self, cursor, user, ids, name, arg, context=None):
        res = {}
        ir_values_obj = self.pool.get('ir.values')
        value_ids = ir_values_obj.search(cursor, user, [
            ('model', '=', self._name), ('key', '=', 'action'),
            ('key2', '=', 'wx_nemu_open'), ('res_id', 'in', ids)],
            context=context)
        values_action = {}
        for value in ir_values_obj.browse(cursor, user, value_ids, context=context):
            values_action[value.res_id] = value.value
        for menu_id in ids:
            res[menu_id] = values_action.get(menu_id, False)
        return res

    def _action_inv(self, cursor, user, menu_id, name, value, arg, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        if self.CONCURRENCY_CHECK_FIELD in ctx:
            del ctx[self.CONCURRENCY_CHECK_FIELD]
        ir_values_obj = self.pool.get('ir.values')
        values_ids = ir_values_obj.search(cursor, user, [
            ('model', '=', self._name), ('key', '=', 'action'),
            ('key2', '=', 'wx_nemu_open'), ('res_id', '=', menu_id)],
            context=context)
        if value and values_ids:
            ir_values_obj.write(cursor, user, values_ids, {'value': value}, context=ctx)
        elif value:
            # no values_ids, create binding
            ir_values_obj.create(cursor, user, {
                'name': u'wx_menuitem',
                'model': self._name,
                'value': value,
                'key': 'action',
                'key2': 'wx_nemu_open',
                'res_id': menu_id,
                }, context=ctx)
        elif values_ids:
            # value is False, remove existing binding
            ir_values_obj.unlink(cursor, user, values_ids, context=ctx)

    
    _name = 'wx.menu'
    _description = u'微信菜单'
    #_order = 
    #_inherit = []
    _columns = {
        'left_ids': fields.one2many('wx.menu.item.left', 'menu_id', '左'),
        'middle_ids': fields.one2many('wx.menu.item.middle', 'menu_id', '中'),
        'right_ids': fields.one2many('wx.menu.item.right', 'menu_id', '右'),
        
        'left': fields.char('左菜单'),
        'left_action': fields.reference('动作', selection=[
            ('wx.action.act_article', u'图文响应'),
            ('wx.action.act_text', u'文本响应'),
            ('wx.action.act_url', u'超链接'),
            ('wx.action.act_custom', u'自定义动作'),
         ]),
                
        'middle': fields.char('中菜单'),
        'middle_action': fields.reference('动作', selection=[
            ('wx.action.act_article', u'图文响应'),
            ('wx.action.act_text', u'文本响应'),
            ('wx.action.act_url', u'超链接'),
            ('wx.action.act_custom', u'自定义动作'),
         ]),
                
        'right': fields.char('右菜单'),
        'right_action': fields.reference('动作', selection=[
            ('wx.action.act_article', u'图文响应'),
            ('wx.action.act_text', u'文本响应'),
            ('wx.action.act_url', u'超链接'),
            ('wx.action.act_custom', u'自定义动作'),
         ]),
        
        'sequence' : fields.integer('Sequence', help="sequence"),
        'child_ids': fields.one2many('wx.menu', 'parent_id', u'子菜单', ),
        'name': fields.char(u'名称', ),
        'parent_id': fields.many2one('wx.menu', u'父菜单', ),
        'action': fields.function(_action, fnct_inv=_action_inv,
            type='reference', string=u'动作',
            selection=[
                ('wx.action.act_article', u'图文响应'),
                ('wx.action.act_text', u'文本响应'),
                ('wx.action.act_url', u'超链接'),
                ('wx.action.act_custom', u'自定义动作'),
            ]),
    }
    #_defaults = {
    #}
    _order = 'sequence'
    
    def create(self, cr, uid, data, context=None):
        menu_id = super(wx_menu, self).create(cr, uid, data, context=context)
        #mydo()
        return menu_id
    
    def unlink(self, cr, uid, ids, context=None):
        self._check_moves(cr, uid, ids, "unlink", context=context)
        return super(wx_menu, self).unlink(cr, uid, ids, context=context)
    
    def write(self, cr, uid, ids, data, context=None):
        result = super(wx_menu, self).write(cr, uid, ids, data, context=context)
        #self.post_write(cr, uid, ids, context=context)
        return result


class wx_user(osv.osv):
    _name = 'wx.user'
    _description = u'微信用户'
    #_order = 
    #_inherit = []
    _columns = {
        'city': fields.char(u'城市', ),
        'country': fields.char(u'国家', ),
        'group_id': fields.many2one('wx.user.group', u'所属组', ),
        'headimgurl': fields.char(u'头像', ),
        'nickname': fields.char(u'昵称', ),
        'openid': fields.char(u'用户标志', ),
        'province': fields.char(u'省份', ),
        'sex': fields.selection([('1',u'男'),('2',u'女')],u'性别', ),
        'subscribe': fields.boolean(u'关注状态', ),
        'subscribe_time': fields.char(u'关注时间', ),
    }
    #_defaults = {
    #}


class wx_user_group(osv.osv):
    _name = 'wx.user.group'
    _description = u'微信用户组'
    #_order = 
    #_inherit = []
    _columns = {
        'count': fields.integer(u'用户数', ),
        'group_id': fields.char(u'组编号', ),
        'group_name': fields.char(u'组名', ),
        'user_ids': fields.one2many('wx.user', 'group_id', u'用户', ),
    }
    #_defaults = {
    #}


