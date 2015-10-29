# coding=utf-8

from ..routes import robot


@robot.subscribe
def subscribe(message):
    serviceid = message.target
    openid = message.source

    return "您终于来了！欢迎关注可友电话"

@robot.unsubscribe
def unsubscribe(message):
    
    serviceid = message.target
    openid = message.source

    return "欢迎下次光临！"
    
@robot.view
def url_view(message):
    print 'obot.view---------',message