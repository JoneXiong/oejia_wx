# coding=utf-8

from openerp import models, fields, api


class wx_articlesreply_article(models.Model):
    _name = 'wx.articlesreply.article'
    _description = u'图文'
    _rec_name = 'title'
    #_order = 
    #_inherit = []

    #articles_id = fields.Many2one('wx.articlesreply', '所属图文回复', )
    description = fields.Char('副标题', required = True, )
    img = fields.Char('图片地址')
    img_file = fields.Binary(string='上传图片', attachment=True)
    img_type = fields.Selection([("url", '图片地址'),("file", '上传图片')], string=u'图片类型')
    title = fields.Char('主标题', required = True, )
    url = fields.Char('跳转链接', required = True, )

    img_show = fields.Html(compute='_get_img_show', string='图片')

    #_defaults = {
    #}

    def get_wx_reply(self, openid=None):
        return {'title': self.title, 'description': self.description, 'image': self.get_img_url(), 'url': self.url}

    @api.multi
    def _get_img_show(self):
        objs = self
        for self in objs:
            self.img_show= '<img src=%s width="100px" height="100px" />'%self.get_img_url()

    def get_img_url(self):
        if self.img_type=='url':
            return self.img
        else:
            base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            return '%s/web/image/wx.articlesreply.article/%s/img_file/'%(base_url, self.id)


class wx_action_act_article(models.Model):
    _name = 'wx.action.act_article'
    _description = u'返回图文'
    #_order = 
    #_inherit = []

    name = fields.Char(u'名称', )
    article_ids = fields.Many2many('wx.articlesreply.article', 'articles_id', u'内容列表', )

    #_defaults = {
    #}

    def get_wx_reply(self, openid=None):
        articles = [article.get_wx_reply(openid) for article in self.article_ids]
        return articles

    @api.multi
    def name_get(self):
        return [(e.id, u'[图文] %s'%e.name) for e in self]


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

    def get_wx_reply(self, openid=None):
        if self.excute_type=='python':
            r = ''
            exec(self.excute_content)
            return r

    @api.multi
    def name_get(self):
        return [(e.id, u'[自定义] %s'%e.name) for e in self]

class wx_action_act_text(models.Model):
    _name = 'wx.action.act_text'
    _description = u'返回文本'
    #_order = 
    #_inherit = []

    name = fields.Char(u'名称', )
    content = fields.Text(u'内容', )

    #_defaults = {
    #}

    def get_wx_reply(self, openid=None):
        return self.content

    @api.multi
    def name_get(self):
        return [(e.id, u'[文本] %s'%e.name) for e in self]

class wx_action_act_url(models.Model):
    _name = 'wx.action.act_url'
    _description = u'URL跳转'
    #_order = 
    #_inherit = []

    name = fields.Char(u'名称', )
    url = fields.Char(u'链接地址', )

    #_defaults = {
    #}
    @api.multi
    def name_get(self):
        return [(e.id, u'[URL链接] %s'%e.name) for e in self]

class wx_action_act_wxa(models.Model):
    _name = 'wx.action.act_wxa'
    _description = u'小程序跳转'

    name = fields.Char(u'描述', )
    appid = fields.Char(u'小程序AppID', default=lambda self: self.env['wx.app.config'].sudo().get_cur().app_id)
    pagepath = fields.Char(u'小程序页面路径', )
    url = fields.Char(u'老版微信备用URL', )

    @api.multi
    def name_get(self):
        return [(e.id, u'[小程序] %s'%e.name) for e in self]


class wx_action_act_media(models.Model):
    _name = 'wx.action.act_media'
    _description = u'返回素材'

    name = fields.Char(u'描述', )
    media_id = fields.Many2one('wx.media','选择素材')

    def get_wx_reply(self, openid=None):
        media_obj = self.media_id
        return {
            'media_type': media_obj.media_type,
            'media_id': media_obj.media_id,
        }

    @api.multi
    def name_get(self):
        return [(e.id, u'[素材] %s'%e.name) for e in self]
