# coding=utf-8
from odoo import release

from . import models

def get_wx_reply_from_aciton(action):
    _name = action._name
    if _name==models.wx_action_act_text._name:
        return action.content
    elif _name==models.wx_action_act_article._name:
        articles = action.article_ids
        return ''
    elif _name==models.wx_action_act_custom._name:
        return ''

DEFAULT_IMG_URL = '/web/static/src/img/placeholder.png'
odoo_ver = release.version_info[0]
if odoo_ver>=15:
    DEFAULT_IMG_URL = '/web/static/img/placeholder.png'
