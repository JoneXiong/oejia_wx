# coding=utf-8
import re
import logging
import base64
import os
import datetime

from werobot.reply import create_reply
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

    def input_handle(message, session):
        from .. import client
        entry = client.wxenv(request.env)
        client = entry
        serviceid = message.target
        openid = message.source
        mtype = message.type
        _logger.info('>>> wx msg: %s'%message.__dict__)
        origin_content = ''
        attachment_ids = []
        if mtype=='image':
            pic_url = message.img
            media_id = message.__dict__.get('MediaId','')
            _logger.info(pic_url)
            _data = get_img_data(pic_url)
            _filename = datetime.datetime.now().strftime("%m%d%H%M%S") + os.path.basename(pic_url)
            attachment = request.env['ir.attachment'].sudo().create({
                'name': '__wx_image|%s'%media_id,
                'datas': base64.encodestring(_data),
                'datas_fname': _filename,
                'res_model': 'mail.compose.message',
                'res_id': int(0)
            })
            attachment_ids.append(attachment.id)
        elif mtype in ['voice']:
            media_id = message.media_id
            media_format = message.format
            r = client.wxclient.download_media(media_id)
            _filename = '%s.%s'%(media_id,media_format)
            _data = r.content
            attachment = request.env['ir.attachment'].sudo().create({
                'name': '__wx_voice|%s'%message.media_id,
                'datas': _data.encode('base64'),
                'datas_fname': _filename,
                'res_model': 'mail.compose.message',
                'res_id': int(0)
            })
            attachment_ids.append(attachment.id)
        elif mtype=='text':
            origin_content = message.content

        content = origin_content.lower()
        rs = request.env()['wx.autoreply'].sudo().search([])
        for rc in rs:
            _key = rc.key.lower()
            if rc.type==1:
                if content==_key:
                    ret_msg = rc.action.get_wx_reply()
                    return create_reply(ret_msg, message=message)
            elif rc.type==2:
                if _key in content:
                    ret_msg = rc.action.get_wx_reply()
                    return create_reply(ret_msg, message=message)
            elif rc.type==3:
                try:
                    flag = re.compile(_key).match(content)
                except:flag=False
                if flag:
                    ret_msg = rc.action.get_wx_reply()
                    return create_reply(ret_msg, message=message)
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
            message_content = origin_content
            request_uid = request.session.uid or openerp.SUPERUSER_ID
            author_id = False  # message_post accept 'False' author_id, but not 'None'
            if request.session.uid:
                author_id = request.env['res.users'].sudo().browse(request.session.uid).partner_id.id
            mail_channel = request.env["mail.channel"].sudo(request_uid).search([('uuid', '=', uuid)], limit=1)
            msg = mail_channel.sudo(request_uid).with_context(mail_create_nosubscribe=True).message_post(author_id=author_id, email_from=mail_channel.anonymous_name, body=message_content, message_type='comment', subtype='mail.mt_comment', content_subtype='plaintext',attachment_ids=attachment_ids)
        if ret_msg:
            return create_reply(ret_msg, message=message)
    robot.add_handler(input_handle, type='text')
    robot.add_handler(input_handle, type='image')
    robot.add_handler(input_handle, type='voice')
