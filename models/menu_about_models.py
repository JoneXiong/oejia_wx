# coding=utf-8

from openerp import models, fields, api
from ..controllers.client import wxclient


ACTION_OPTION = [
        ('wx.action.act_article', '图文响应'),
        ('wx.action.act_text', '文本响应'),
        ('wx.action.act_custom', '自定义动作'),
     ]

MENU_ACTION_OPTION = ACTION_OPTION + [('wx.action.act_url', '跳转链接')]

class menu_item_base(models.AbstractModel):
     
    _name = 'wx.menu.item.base'
     
    menu_id = fields.Many2one('wx.menu', string='所属微信菜单', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', help="sequence")
    name = fields.Char('子菜单', )
    action = fields.Reference(string='动作', selection=MENU_ACTION_OPTION)

    _order = 'sequence'

class menu_item_left(models.Model):
    _name = 'wx.menu.item.left'
    _description = u'左菜单项'
    _inherit = 'wx.menu.item.base'

class menu_item_middle(models.Model):
    _name = 'wx.menu.item.middle'
    _description = u'中菜单项'
    _inherit = 'wx.menu.item.base'
    
class menu_item_right(models.Model):
    _name = 'wx.menu.item.right'
    _description = u'右菜单项'
    _inherit = 'wx.menu.item.base'

class wx_menu(models.Model):
    
    _name = 'wx.menu'
    _description = u'微信菜单'
    #_order = 
    #_inherit = []
    
    name = fields.Char('名称', )
    left_ids = fields.One2many('wx.menu.item.left', 'menu_id', '左')
    middle_ids = fields.One2many('wx.menu.item.middle', 'menu_id', '中')
    right_ids = fields.One2many('wx.menu.item.right', 'menu_id', '右')
    left = fields.Char('左菜单')
    left_action = fields.Reference(string='动作', selection=MENU_ACTION_OPTION)
    middle = fields.Char('中菜单')
    middle_action = fields.Reference(string='动作', selection=MENU_ACTION_OPTION)
    right = fields.Char('右菜单')
    right_action = fields.Reference(string='动作', selection=MENU_ACTION_OPTION)
    sequence = fields.Integer('Sequence', help="sequence")
    
    mtype = fields.Selection([(1,'公众号'),(2,'企业号')], string='类型', default=1)

    #_defaults = {
    #}
    _order = 'sequence'
    
    def _get_menu_action(self, name, action):
        if action and action._name=='wx.action.act_url':
            m_dict = {
                      'type': 'view',
                      'name': name,
                      'url': action.url
                      }
        else:
            m_dict = {
                      'type': 'click',
                      'name': name,
                      'key': action and action._name+ ',' + str(action.id) or ',0'
                      }
        return m_dict
    
    def _get_menu_item(self, name, action, childs):
        if childs:
            child_list = []
            for child in childs:
                child_dict = self._get_menu_action(child.name, child.action)
                child_list.append(child_dict)
            return {
                    'name': name,
                    'sub_button': child_list
                    }
        else:
            return self._get_menu_action(name, action)
        
    @api.one
    def do_active(self):
        buttons = []
        if self.left:
            buttons.append(self._get_menu_item(self.left, self.left_action, self.left_ids))
        if self.middle:
            buttons.append(self._get_menu_item(self.middle, self.middle_action, self.middle_ids))
        if self.right:
            buttons.append(self._get_menu_item(self.right, self.right_action, self.right_ids))
        menu_data =  {'button': buttons}
        wxclient.create_menu(menu_data)
