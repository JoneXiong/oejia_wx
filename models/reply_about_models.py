# coding=utf-8

from openerp import models, fields, api


class wx_articlesreply_article(models.Model):
    _name = 'wx.articlesreply.article'
    _description = u'图文'
    _rec_name = 'title'
    #_order = 
    #_inherit = []
    
    #articles_id = fields.Many2one('wx.articlesreply', '所属图文回复', )
    description = fields.Char('描述', required = True, )
    img = fields.Char('图片地址', required = True, )
    title = fields.Char('标题', required = True, )
    url = fields.Char('跳转链接', required = True, )
    
    img_show = fields.Html(compute='_get_img_show', string='图片')
        
    #_defaults = {
    #}
    
    def get_wx_reply(self):
        return [self.title, self.description, self.img, self.url]
    
    @api.one
    def _get_img_show(self):
        self.img_show= '<img src=%s width="100px" height="100px" />'%self.img


class wx_action_act_article(models.Model):
    _name = 'wx.action.act_article'
    _description = u'返回图文动作'
    #_order = 
    #_inherit = []

    name = fields.Char(u'名称', )
    article_ids = fields.Many2many('wx.articlesreply.article', 'articles_id', u'内容列表', )
        
    #_defaults = {
    #}
    
    def get_wx_reply(self):
        articles = [article.get_wx_reply() for article in self.article_ids]
        return articles


class wx_action_act_custom(models.Model):
    _name = 'wx.action.act_custom'
    _description = u'自定义动作'
    #_order = 
    #_inherit = []

    name = fields.Char('名称', )
    excute_content = fields.Text('执行内容', )
    excute_type = fields.Selection([('python','Python')],'执行方式', )

    #_defaults = {
    #}

    def get_wx_reply(self):
        if self.excute_type=='python':
            return eval(self.excute_content)

class wx_action_act_text(models.Model):
    _name = 'wx.action.act_text'
    _description = u'返回文本动作'
    #_order = 
    #_inherit = []

    name = fields.Char(u'名称', )
    content = fields.Text(u'内容', )

    #_defaults = {
    #}
    
    def get_wx_reply(self):
        return self.content

class wx_action_act_url(models.Model):
    _name = 'wx.action.act_url'
    _description = u'超链接动作'
    #_order = 
    #_inherit = []
    
    name = fields.Char(u'名称', )
    url = fields.Char(u'链接地址', )
    
    #_defaults = {
    #}