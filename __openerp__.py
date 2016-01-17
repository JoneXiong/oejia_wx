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
             ],
    'depends' : ['im_livechat'],
    'installable': True,
    'active': False,
    'web': True,
}
