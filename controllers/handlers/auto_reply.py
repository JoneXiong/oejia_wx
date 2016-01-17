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
    registry = request.env()
    if not client.UUID_OPENID.has_key(db):
        client.UUID_OPENID[db] = {}
    if not uuid:
        channel_id = 2
        info = client.wxclient.get_user_info(openid)
        anonymous_name = info.get('nickname','微信网友')
        reg = openerp.modules.registry.RegistryManager.get(db)
        session_info = reg.get('im_livechat.channel').get_channel_session(cr, uid, channel_id, anonymous_name, context=context)
        uuid = session_info['uuid']
        session["uuid"] = uuid
        ret_msg = '请稍后，正在分配客服为您解答'
    client.UUID_OPENID[db][uuid] = openid

    message_type = "message"
    message_content = content
    registry, cr, uid, context = request.registry, request.cr, request.session.uid, request.context
    message_id = registry["im_chat.message"].post(cr,openerp.SUPERUSER_ID,uid, uuid, message_type, message_content, context=context)
    return ret_msg
