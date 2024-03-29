# coding=utf-8
import logging

from odoo.http import request

_logger = logging.getLogger(__name__)

if True:
    def subscribe(request, message):
        _logger.info('>>> wx msg: %s', message.__dict__)
        entry = request.entry
        serviceid = message.target
        openid = message.source

        env = request.env()
        rs = env['wx.user'].sudo().search( [('openid', '=', openid)] )
        if not rs.exists():
            info = entry.wxclient.user.get(openid)
            info['group_id'] = str(info['groupid'])
            rs = env['wx.user'].sudo().create(info)
        else:
            rs.write({'subscribe': True})
        ret = rs.deal_scene(message.__dict__['_data'].get('EventKey'))
        if ret:
            return ret

        if entry.subscribe_auto_msg:
            ret_msg = entry.subscribe_auto_msg
        else:
            ret_msg = "您终于来了！欢迎关注"

        return ret_msg

    def scan(request, message):
        _logger.info('>>> wx msg: %s', message.__dict__)
        entry = request.entry
        openid = message.source

        env = request.env()
        rs = env['wx.user'].sudo().search( [('openid', '=', openid)] )
        if not rs.exists():
            info = entry.wxclient.user.get(openid)
            info['group_id'] = str(info['groupid'])
            rs = env['wx.user'].sudo().create(info)
        ret = rs.deal_scene(message.__dict__['_data'].get('EventKey'))
        if ret:
            return ret
        else:
            return ''

    def unsubscribe(request, message):

        serviceid = message.target
        openid = message.source
        env = request.env()
        rs = env['wx.user'].sudo().search( [('openid', '=', openid)] )
        if rs.exists():
            rs.write({'subscribe': False})

        return ""

    def url_view(request, message):
        _logger.debug('>>> event.view %s', message)
        return ''
