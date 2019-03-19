# coding=utf-8

from werobot.reply import create_reply
from .. import client
from openerp.http import request

def main(robot):

    @robot.subscribe
    def subscribe(message):
        from .. import client
        entry = client.wxenv(request.env)
        client = entry
        serviceid = message.target
        openid = message.source

        info = client.wxclient.get_user_info(openid)
        info['group_id'] = str(info['groupid'])
        env = request.env()
        rs = env['wx.user'].sudo().search( [('openid', '=', openid)] )
        if not rs.exists():
            env['wx.user'].sudo().create(info)

        ret_msg = "您终于来了！欢迎关注"
        return create_reply(ret_msg, message=message)

    @robot.unsubscribe
    def unsubscribe(message):

        serviceid = message.target
        openid = message.source
        env = request.env()
        rs = env['wx.user'].sudo().search( [('openid', '=', openid)] )
        if rs.exists():
            rs.unlink()

        return ""

    @robot.view
    def url_view(message):
        print('obot.view---------%s'%message)
