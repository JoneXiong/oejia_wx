# coding=utf-8

from ..routes import robot

@robot.text
def input_handle(message, session):
    content = message.content.lower()
    serviceid = message.target
    openid = message.source
    
    if content.startswith('e'):
        return content