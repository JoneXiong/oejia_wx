# coding=utf-8
import datetime
import base64
import os

import openerp

from ...rpc import corp_client


def kf_handler(request, msg):
    client = corp_client.corpenv(request.env)
    openid = msg.source
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
        uuid = client.get_uuid_from_uid(uid)

    if not uuid:
        # 识别为客服型消息
        kf_flag = True
        # 客服会话ID
        uuid = client.OPENID_UUID.get(openid, None)

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
        anonymous_name = corp_user.userid

        channel = request.env.ref('oejia_wx.channel_corp')
        channel_id = channel.id

        session_info = request.env['im_livechat.channel'].sudo().get_mail_channel(channel_id, anonymous_name)
        if session_info:
            uuid = session_info['uuid']
            client.OPENID_UUID[openid] = uuid
            client.UUID_OPENID[uuid] = openid
            corp_user.write({'last_uuid': uuid})
            request.env['wx.corpuser.uuid'].sudo().create({'userid': openid, 'uuid': uuid})
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
                'datas': _data.encode('base64'),
                'datas_fname': _filename,
                'res_model': 'mail.compose.message',
                'res_id': int(0)
            })
            attachment_ids.append(attachment.id)
        elif mtype=='text':
            message_content = msg.content

        message_type = 'comment'

        author_id = False  # message_post accept 'False' author_id, but not 'None'
        if request.session.uid:
            author_id = request.env['res.users'].sudo().browse(from_uid).partner_id.id
        else:
            author_id = uid
        if kf_flag:
            author_id = False
        mail_channel = request.env["mail.channel"].sudo().search([('uuid', '=', uuid)], limit=1)
        message = mail_channel.sudo().with_context(mail_create_nosubscribe=True).message_post(author_id=author_id, email_from=mail_channel.anonymous_name, body=message_content, message_type=message_type, subtype='mail.mt_comment', content_subtype='plaintext', attachment_ids=attachment_ids)
    return ret_msg

