# coding=utf-8
import datetime

import openerp

from ...rpc import corp_client as client


def kf_handler(request, content, wx_id):
    openid = wx_id
    # 获取关联的系统用户
    uid = client.OPENID_UID.get(openid, None)
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
        _key = '%s-%s'%(request.db, uid)
        if _key in client.UID_UUID:
            _data = client.UID_UUID[_key]
            _now = datetime.datetime.now()
            if _now - _data['last_time']<=  datetime.timedelta(seconds=10*60):
                uuid = _data['uuid']
    if not uuid:
        kf_flag = True
        uuid = client.OPENID_UUID.get(openid, None)
    
    ret_msg = ''
    if not client.UUID_OPENID.has_key(request.db):
        client.UUID_OPENID[request.db] = {}
    
    if not uuid:
        Param = request.env()['ir.config_parameter'].sudo()
        channel_id = Param.get_param('Corp_Channel') or 0
        channel_id = int(channel_id)
        
        info = {}#client.wxclient.get_user_info(openid)
        anonymous_name = info.get('nickname', u'微信网友 %s'%wx_id)
        
        session_info = request.env['im_livechat.channel'].sudo().get_mail_channel(channel_id, anonymous_name)
        if session_info:
            uuid = session_info['uuid']
            client.OPENID_UUID[openid] = uuid
            client.UUID_OPENID[request.db][uuid] = openid
        ret_msg = u'请稍后，正在分配客服为您解答'
    
    if uuid:
        message_type = 'comment'
        message_content = content
        if kf_flag:
            author_id = False
        else:
            author_id = uid
        author_id = False  # message_post accept 'False' author_id, but not 'None'
        if request.session.uid:
            author_id = request.env['res.users'].sudo().browse(from_uid).partner_id.id
        mail_channel = request.env["mail.channel"].sudo().search([('uuid', '=', uuid)], limit=1)
        message = mail_channel.sudo().with_context(mail_create_nosubscribe=True).message_post(author_id=author_id, email_from=False, body=message_content, message_type=message_type, subtype='mail.mt_comment', content_subtype='plaintext')
    return ret_msg
    
