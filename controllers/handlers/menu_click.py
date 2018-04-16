# coding=utf-8

from openerp.http import request

def main(robot):

    @robot.click
    def onclick(message, session):
        _name, action_id = message.key.split(',')
        action_id = int(action_id)
        if _name:
            action = request.env()[_name].sudo().browse(action_id)
            return action.get_wx_reply()
