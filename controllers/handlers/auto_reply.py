# coding=utf-8
import re

from ..routes import robot
from openerp.http import request
import openerp
from .. import client


@robot.text
def input_handle(message, session):
    content = message.content.lower()
    serviceid = message.target
    openid = message.source
    
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
    uuid = session.get("uuid", None)
    ret_msg = ''
    cr, uid, context, db = request.cr, request.uid or openerp.SUPERUSER_ID, request.context, request.db
    if not client.UUID_OPENID.has_key(db):
        client.UUID_OPENID[db] = {}
    if not uuid:
        Param = request.env()['ir.config_parameter']
        channel_id = Param.get_param('wx_channel') or 0
        channel_id = int(channel_id)
        
        info = client.wxclient.get_user_info(openid)
        anonymous_name = info.get('nickname','微信网友')
        
        reg = openerp.modules.registry.RegistryManager.get(db)
        session_info = request.env["im_livechat.channel"].get_mail_channel(channel_id, anonymous_name)
        if session_info:
            uuid = session_info['uuid']
            session["uuid"] = uuid
        ret_msg = '请稍后，正在分配客服为您解答'
    
    if uuid:
        client.UUID_OPENID[db][uuid] = openid
        
        message_type = "message"
        message_content = content
        request_uid = request.session.uid or openerp.SUPERUSER_ID
        author_id = False  # message_post accept 'False' author_id, but not 'None'
        if request.session.uid:
            author_id = request.env['res.users'].sudo().browse(request.session.uid).partner_id.id
        mail_channel = request.env["mail.channel"].sudo(request_uid).search([('uuid', '=', uuid)], limit=1)
        message = mail_channel.sudo(request_uid).with_context(mail_create_nosubscribe=True).message_post(author_id=author_id, email_from=False, body=message_content, message_type='comment', subtype='mail.mt_comment', content_subtype='plaintext')

    return ret_msg
