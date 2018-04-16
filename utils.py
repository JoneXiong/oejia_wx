# coding=utf-8

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
