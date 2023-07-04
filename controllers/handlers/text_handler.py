# coding=utf-8
import datetime
import base64
import os
import logging

import odoo


_logger = logging.getLogger(__name__)

def kf_handler(request, msg):
    entry = request.entry
    client = entry
    openid = msg.source
    if msg.id==entry.OPENID_LAST.get(openid):
        _logger.info('>>> 重复的微信消息')
        return ''
    entry.OPENID_LAST[openid] = msg.id
    # 获取关联的系统用户
    uid = client.OPENID_UID.get(openid, False)
    if not uid:
        objs = request.env['wx.corpuser'].sudo().search( [ ('userid', '=', openid), ('corp_config_id', '=', entry.entry_id) ] )
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
        rs = request.env['wx.corpuser'].sudo().search( [('userid', '=', openid), ('corp_config_id', '=', entry.entry_id)] )
        if not rs.exists():
            corp_user = request.env['wx.corpuser'].sudo().create({
                '_from_subscribe': True,
                'name': openid,
                'userid': openid,
                'weixinid': openid,
                'corp_config_id': entry.entry_id,
            })
        else:
            corp_user = rs[0]
        anonymous_name = u'%s [企业微信]'%corp_user.userid

        channel = request.env.ref('oejia_wx.channel_corp').sudo()

        session_info, ret_msg = request.env['im_livechat.channel'].sudo().create_mail_channel(channel, anonymous_name, msg.content, record_uuid, entry=entry)
        if session_info:
            uuid = session_info['uuid']
            client.create_uuid_for_openid(openid, uuid)
            if not record_uuid:
                corp_user.update_last_uuid(uuid)

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

        request_uid = request.session.uid or odoo.SUPERUSER_ID
        author_id = False  # message_post accept 'False' author_id, but not 'None'
        if request.session.uid:
            author_id = request.env['res.users'].sudo().browse(request.session.uid).partner_id.id
        else:
            author_id = uid
        if kf_flag:
            author_id = False
        mail_channel = request.env["mail.channel"].sudo().search([('uuid', '=', uuid)], limit=1)
        if not mail_channel:
            _logger.info('>>> mail_channel is null, uuid %s is invalid', uuid)
            entry.delete_uuid(uuid)
            del entry.OPENID_LAST[openid]
            if attachment_ids:
                request.env['ir.attachment'].sudo().search([('id', 'in', attachment_ids)]).unlink()
            return kf_handler(request, msg)
        message = mail_channel.with_user(request_uid).with_context(mail_create_nosubscribe=True).message_post(author_id=author_id, email_from=mail_channel.anonymous_name, body=message_content, message_type=message_type, subtype_xmlid='mail.mt_comment', content_subtype='plaintext', attachment_ids=attachment_ids)
    return ret_msg

