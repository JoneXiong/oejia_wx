# coding=utf-8
import datetime
import base64
import os
import logging

import openerp

from ...rpc import corp_client

_logger = logging.getLogger(__name__)

def kf_handler(request, msg):
    client = corp_client.corpenv(request.env)
    openid = msg.source
    entry = client
    if msg.id==entry.OPENID_LAST.get(openid):
        _logger.info('>>> 重复的微信消息')
        return ''
    entry.OPENID_LAST[openid] = msg.id
    # 获取关联的系统用户
    uid = client.OPENID_UID.get(openid, False)
    if not uid:
        objs = request.env['wx.corpuser'].sudo().search( [ ('userid', '=', openid) ] )
        if objs.exists():
            corpuser_id = objs[0].id
            objs2 = request.env['res.partner'].sudo().search( [ ('wxcorp_user_id', '=', corpuser_id) ] )
            if objs2.exists():
                uid = objs2[0].id
                client.OPENID_UID[openid] = uid

    uuid = None
    kf_flag = False
    if uid:
        try:
            uuid = client.get_uuid_from_uid(uid)
        except KeyError:
            uuid = None

    if not uuid:
        # 识别为客服型消息
        kf_flag = True
        # 客服会话ID
        uuid, record_uuid = client.get_uuid_from_openid(openid)

    ret_msg = ''

    if not uuid:
        # 客服消息第一次发过来时
        rs = request.env['wx.corpuser'].sudo().search( [('userid', '=', openid)] )
        if not rs.exists():
            corp_user = request.env['wx.corpuser'].sudo().create({
                '_from_subscribe': True,
                'name': openid,
                'userid': openid,
                'weixinid': openid
            })
        else:
            corp_user = rs[0]
        anonymous_name = '%s [企业微信]'%corp_user.userid

        channel = request.env.ref('oejia_wx.channel_corp')
        channel_id = channel.id

        session_info = request.env['im_livechat.channel'].sudo().create_mail_channel(channel_id, anonymous_name, msg.content, record_uuid)
        if session_info:
            uuid = session_info['uuid']
            client.create_uuid_for_openid(openid, uuid)
            if not record_uuid:
                corp_user.update_last_uuid(uuid)
        ret_msg = channel.default_message

    if uuid:
        message_content = ''

        mtype = msg.type
        attachment_ids = []
        if mtype in ['image', 'voice']:
            media_id = msg.media_id
            r = client.client.media.download(media_id)
            if mtype=='image':
                _filename = '%s_%s'%(datetime.datetime.now().strftime("%m%d%H%M%S"), media_id)
            else:
                _filename = '%s.%s'%(media_id,msg.format)
            _data = r.content
            attachment = request.env['ir.attachment'].sudo().create({
                'name': '__wx_voice|%s'%msg.media_id,
                'datas': base64.encodestring(_data),
                'datas_fname': _filename,
                'res_model': 'mail.compose.message',
                'res_id': int(0)
            })
            attachment_ids.append(attachment.id)
        elif mtype=='text':
            message_content = msg.content
            if message_content.startswith('@'):
                sid = message_content[1:]
                if sid.isdigit():
                    ret = client.set_uid_cur_sid(uid, int(sid))
                    if not ret:
                        return u'已切换为会话%s'%sid
        elif mtype=='location':
            message_content = '对方发送位置: %s 纬度为：%s 经度为：%s'%(msg.label, msg.location_x, msg.location_y)

        message_type = 'comment'

        author_id = False  # message_post accept 'False' author_id, but not 'None'
        if request.session.uid:
            author_id = request.env['res.users'].sudo().browse(request.session.uid).partner_id.id
        else:
            author_id = uid
        if kf_flag:
            author_id = False
        mail_channel = request.env["mail.channel"].sudo().search([('uuid', '=', uuid)], limit=1)
        message = mail_channel.sudo().with_context(mail_create_nosubscribe=True).message_post(author_id=author_id, email_from=mail_channel.anonymous_name, body=message_content, message_type=message_type, subtype='mail.mt_comment', content_subtype='plaintext', attachment_ids=attachment_ids)
    return ret_msg

