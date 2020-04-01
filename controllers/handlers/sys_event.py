# coding=utf-8
import logging

from werobot.reply import create_reply

from openerp.http import request

_logger = logging.getLogger(__name__)

if True:
    def subscribe(request, message):
        _logger.info('>>> wx msg: %s', message.__dict__)
        entry = request.entry
        serviceid = message.target
        openid = message.source

        info = entry.wxclient.user.get(openid)
        info['group_id'] = str(info['groupid'])
        env = request.env()
        rs = env['wx.user'].sudo().search( [('openid', '=', openid)] )
        if not rs.exists():
            qrscene = message.__dict__.get('EventKey')
            if qrscene:
                _list = qrscene.split('=')
                if len(_list)>1:
                    inviter_id = _list[1]
                    info['inviter_id'] = int(inviter_id)
            env['wx.user'].sudo().create(info)
        else:
            rs.write({'subscribe': True})

        if entry.subscribe_auto_msg:
            ret_msg = entry.subscribe_auto_msg
        else:
            ret_msg = "您终于来了！欢迎关注"

        return ret_msg

    def unsubscribe(request, message):

        serviceid = message.target
        openid = message.source
        env = request.env()
        rs = env['wx.user'].sudo().search( [('openid', '=', openid)] )
        if rs.exists():
            rs.write({'subscribe': False})

        return ""

    def url_view(request, message):
        print('obot.view---------%s'%message)
