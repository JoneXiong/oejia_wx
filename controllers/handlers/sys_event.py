# coding=utf-8

from ..routes import robot
from .. import client
from openerp.http import request


@robot.subscribe
def subscribe(message):
    serviceid = message.target
    openid = message.source

    info = client.wxclient.get_user_info(openid)
    info['group_id'] = str(info['groupid'])
    env = request.env()
    rs = env['wx.user'].sudo().search( [('openid', '=', openid)] )
    if not rs.exists():
        env['wx.user'].sudo().create(info)
    
    return "您终于来了！欢迎关注"

@robot.unsubscribe
def unsubscribe(message):
    
    serviceid = message.target
    openid = message.source
    env = request.env()
    rs = env['wx.user'].sudo().search( [('openid', '=', openid)] )
    if rs.exists():
        rs.unlink()
                        
    return "欢迎下次光临！"
    
@robot.view
def url_view(message):
    print 'obot.view---------',message