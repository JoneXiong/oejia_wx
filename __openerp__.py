# -*- coding: utf-8 -*-

{
    'name': 'WeChat',
    'version': '1.0.0',
    'category': 'Social Network',
    'summary': '企业微信公众号的接入与管理',
    'author': 'Oejia',
    'website': 'http://www.oejia.net/',
    'depends': ['web'],
    'application': True,
    'auto_data_include': ['views'],
    'data': [
             'data/wx_init_data.xml',
             'data/oejia_wx.xml',
             'views/parent_menus.xml',
             'views/wx_inherit_ext.xml',

             'views/wx_action_act_article_views.xml',
             'views/wx_action_act_custom_views.xml',
             'views/wx_action_act_text_views.xml',
             'views/wx_articlesreply_article_views.xml',
             'views/wx_autoreply_views.xml',
             'views/wx_config_settings_views.xml',
             'views/wx_menu_item_left_views.xml',
             'views/wx_menu_item_middle_views.xml',
             'views/wx_menu_item_right_views.xml',
             'views/wx_menu_views.xml',
             'views/wx_user_group_views.xml',
             'views/wx_user_views.xml',
             'views/wx_config_corpsettings_views.xml',
             'views/wx_corpuser_views.xml',
             ],
    'qweb': [
        'static/src/xml/oejia_wx.xml'
    ],
    'depends' : ['im_livechat'],
    'installable': True,
    'active': False,
    'web': True,
}
