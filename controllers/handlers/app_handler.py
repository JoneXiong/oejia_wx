# coding=utf-8
import datetime
import logging
import base64

import openerp

from ...rpc import app_client

_logger = logging.getLogger(__name__)


def app_kf_handler(request, message):
    entry = app_client.appenv(request.env)
    client = entry
    openid = message.source
    mtype = message.type

    origin_content = ''
    attachment_ids = []

    if mtype=='image':
        media_id = message.media_id
        r = entry.client.media.download(media_id)
        _filename = '%s_%s'%(datetime.datetime.now().strftime("%m%d%H%M%S"), media_id)
        _data = r.content
        attachment = request.env['ir.attachment'].sudo().create({
            'name': '__wx_image|%s'%message.media_id,
            'datas': base64.encodestring(_data),
            'datas_fname': _filename,
            'res_model': 'mail.compose.message',
            'res_id': int(0)
        })
        attachment_ids.append(attachment.id)
    elif mtype=='text':
        origin_content = message.content

    #客服对话
    uuid, record_uuid = entry.get_uuid_from_openid(openid)
    ret_msg = ''

    if not uuid:
        rs = request.env['wx.user'].sudo().search( [('openid', '=', openid)] )
        #if not rs.exists():
        #    info = entry.wxclient.get_user_info(openid)
        #    info['group_id'] = ''
        #    wx_user = request.env['wx.user'].sudo().create(info)
        #else:
        #    wx_user = rs[0]
        anonymous_name = "%s [小程序]"%openid[-4:]#wx_user.nickname

        channel = request.env.ref('oejia_wx.channel_app')
        channel_id = channel.id

        session_info, ret_msg = request.env["im_livechat.channel"].create_mail_channel(channel_id, anonymous_name, origin_content, record_uuid)
        _logger.info('>>> get session %s %s'%(session_info, ret_msg))
        if session_info:
            uuid = session_info['uuid']
            entry.create_uuid_for_openid(openid, uuid)
            #wx_user.write({'last_uuid': uuid})
            #request.env['wx.user.uuid'].sudo().create({'openid': openid, 'uuid': uuid})

    if uuid:
        request_uid = request.session.uid or openerp.SUPERUSER_ID
        author_id = False  # message_post accept 'False' author_id, but not 'None'
        if request.session.uid:
            author_id = request.env['res.users'].sudo().browse(request.session.uid).partner_id.id

        mail_channel = request.env["mail.channel"].sudo(request_uid).search([('uuid', '=', uuid)], limit=1)
        message = mail_channel.sudo(request_uid).with_context(mail_create_nosubscribe=True).message_post(author_id=author_id, email_from=mail_channel.anonymous_name, body=origin_content, message_type='comment', subtype='mail.mt_comment', content_subtype='plaintext',attachment_ids=attachment_ids)

    if ret_msg:
        entry.client.message.send_text(openid, ret_msg)
    return ret_msg

