# coding=utf-8

from ..routes import robot
from openerp.http import request


@robot.click
def onclick(message, session):
    action_id = message.key.replace('menu_action_id_', '')
    _name, action_id = message.key.split(',')
    action_id = int(action_id)
    if _name:
        action = request.env()[_name].browse(action_id)
        return action.get_wx_reply()