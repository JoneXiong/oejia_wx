# coding=utf-8

from werobot.client import Client, ClientException
from openerp import exceptions

wxclient = Client('appid_xxxxxxxxxxxxxxx', 'appsecret_xxxxxxxxxxxxxx')

UUID_OPENID = {}

def send_text(openid,text):
    try:
        wxclient.send_text_message(openid, text)
    except ClientException, e:
        raise exceptions.UserError(u'发送失败 %s'%e)

def chat_send(db,uuid, msg):
    _dict = UUID_OPENID.get(db,None)
    if _dict:
        openid = _dict.get(uuid,None)
        if openid:
            send_text(openid, msg)
    return -1
