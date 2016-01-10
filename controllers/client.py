# coding=utf-8

from werobot.client import Client

wxclient = Client('appid_xxxxxxxxxxxxxxx', 'appsecret_xxxxxxxxxxxxxx')

UUID_OPENID = {}

def send_text(openid,text):
    wxclient.send_text_message(openid, text)

def chat_send(db,uuid, msg):
    _dict = UUID_OPENID.get(db,None)
    if _dict:
        openid = _dict.get(uuid,None)
        if openid:
            send_text(openid, msg)
    return -1