# coding=utf-8
import re
import logging
import base64
import os

from openerp.http import request
import openerp
from .. import client

_logger = logging.getLogger(__name__)


def get_img_data(pic_url):
    import requests
    headers = {
	'Accept': 'textml,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
	'Cache-Control': 'no-cache',
	'Host': 'mmbiz.qpic.cn',
	'Pragma': 'no-cache',
	'Connection': 'keep-alive',
	'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    }
    r = requests.get(pic_url,headers=headers,timeout=50)
    return r.content

def main(robot):

    #@robot.text
    def input_handle(message, session):
        from .. import client
        entry = client.wxenv(request.env)
        client = entry
        content = message.content.lower()
        serviceid = message.target
        openid = message.source
        _logger.info('>>> wx msg: %s'%message)
        #_logger.info('>>> wx text msg: %s'%content)
        pic_url = message.img
        attachment_ids = []
        if pic_url:
            _data = get_img_data(pic_url)
            _filename = os.path.basename(pic_url)
            attachment = Model.create({
                'name': _filename,
                'datas': base64.encodestring(_data),
                'datas_fname': _filename,
                'res_model': 'mail.compose.message',
                'res_id': int(0)
            })
            attachment_ids.append(attachment.id)

        rs = request.env()['wx.autoreply'].sudo().search([])
        for rc in rs:
            if rc.type==1:
                if content==rc.key:
                    return rc.action.get_wx_reply()
            elif rc.type==2:
                if rc.key in content:
                    return rc.action.get_wx_reply()
            elif rc.type==3:
                try:
                    flag = re.compile(rc.key).match(content)
                except:flag=False
                if flag:
                    return rc.action.get_wx_reply()
        #客服对话
        uuid = client.OPENID_UUID.get(openid, None)
        ret_msg = ''
        cr, uid, context, db = request.cr, request.uid or openerp.SUPERUSER_ID, request.context, request.db

        if not uuid:
            rs = request.env['wx.user'].sudo().search( [('openid', '=', openid)] )
            if not rs.exists():
                info = client.wxclient.get_user_info(openid)
                info['group_id'] = ''
                wx_user = request.env['wx.user'].sudo().create(info)
            else:
                wx_user = rs[0]
            anonymous_name = wx_user.nickname

            channel = request.env.ref('oejia_wx.channel_wx')
            channel_id = channel.id

            session_info, ret_msg = request.env["im_livechat.channel"].create_mail_channel(channel_id, anonymous_name, content)
            if session_info:
                uuid = session_info['uuid']
                client.OPENID_UUID[openid] = uuid
                client.UUID_OPENID[uuid] = openid
                wx_user.write({'last_uuid': uuid})
                request.env['wx.user.uuid'].sudo().create({'openid': openid, 'uuid': uuid})

        if uuid:
            message_type = "message"
            message_content = message.content
            request_uid = request.session.uid or openerp.SUPERUSER_ID
            author_id = False  # message_post accept 'False' author_id, but not 'None'
            if request.session.uid:
                author_id = request.env['res.users'].sudo().browse(request.session.uid).partner_id.id
            mail_channel = request.env["mail.channel"].sudo(request_uid).search([('uuid', '=', uuid)], limit=1)
            message = mail_channel.sudo(request_uid).with_context(mail_create_nosubscribe=True).message_post(author_id=author_id, email_from=False, body=message_content, message_type='comment', subtype='mail.mt_comment', content_subtype='plaintext',attachment_ids=attachment_ids)

        return ret_msg
    robot.add_handler(input_handle, type='text')
    robot.add_handler(input_handle, type='image')
